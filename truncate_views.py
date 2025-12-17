
import os

views_path = r'c:\Users\HP\farm_project\core\views.py'

mpesa_code = """
# Error Handlers
def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

@csrf_exempt
def mpesa_callback(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            
            print(f"M-Pesa Callback Received for Order {order_id}: Code {result_code}")

            payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
            if not payment:
                print(f"Payment not found for request ID: {checkout_request_id}")
                return HttpResponse("Payment Not Found", status=404)
            
            if result_code == 0:
                # Success
                metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                receipt_number = next((item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber'), None)
                
                payment.status = 'COMPLETED'
                payment.transaction_id = receipt_number
                payment.save()
                
                order = payment.order
                order.status = 'CONFIRMED'
                order.confirmed_at = timezone.now()
                order.save()
                print(f"Payment Confirmed: {receipt_number}")
            else:
                # Failure
                payment.status = 'FAILED'
                payment.save()
                print(f"Payment Failed: {stk_callback.get('ResultDesc')}")

        except Exception as e:
            print(f"Callback Error: {e}")
            
    return HttpResponse("OK")
"""

try:
    with open(views_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Keep lines up to 2375
    # Python list slicing is 0-indexed, so 2375 lines is lines[:2375]
    # Check if line 2375 is around where we want to cut.
    # Previous view showed line 2375 as "return render(request, 'update_order_status.html', context)"
    
    clean_lines = lines[:2376] # Keep up to 2376 to include the return statement
    
    content = "".join(clean_lines) + "\n\n" + mpesa_code
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("SUCCESS: views.py truncated and cleaned.")
    
except Exception as e:
    print(f"ERROR: {e}")
