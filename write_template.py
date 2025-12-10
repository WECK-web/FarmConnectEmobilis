
content = """{% extends 'base.html' %}

{% block content %}
<div class="row mb-4">
    <div class="col-12 text-center">
        <h1 class="display-4">Available Produce</h1>
        <p class="lead">Connect with local farmers and help reduce food waste.</p>
    </div>
</div>

<!-- Search and Filter Section -->
<div class="row mb-4">
    <div class="col-md-8 mx-auto">
        <form action="{% url 'home' %}" method="get" class="d-flex gap-2">
            <input type="text" name="q" class="form-control" placeholder="Search for produce..."
                value="{{ request.GET.q|default:'' }}">
            <select name="category" class="form-select" style="width: auto;">
                <option value="">All Categories</option>
                {% for cat in categories %}
                <option value="{{ cat.id }}" {% if cat.id == selected_category %}selected{% endif %}>{{ cat.name }}</option>
                {% endfor %}
            </select>
            <button type="submit" class="btn btn-primary">Search</button>
        </form>
    </div>
</div>

<div class="row row-cols-1 row-cols-md-3 g-4">
    {% for listing in listings %}
    <div class="col">
        <div class="card h-100 shadow-sm">
            {% if listing.image %}
            <img src="{{ listing.image.url }}" class="card-img-top" alt="{{ listing.title }}"
                style="height: 200px; object-fit: cover;">
            {% else %}
            <div class="card-img-top bg-secondary text-white d-flex align-items-center justify-content-center"
                style="height: 200px;">
                <span>No Image</span>
            </div>
            {% endif %}
            <div class="card-body">
                <h5 class="card-title">{{ listing.title }}</h5>
                <p class="card-text text-muted">
                    {{ listing.category.name }} |
                    <a href="{% url 'farmer_profile' listing.seller.username %}" class="text-decoration-none">
                        {{ listing.seller.username }}
                    </a>
                </p>
                <p class="card-text">{{ listing.description|truncatewords:20 }}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <span class="badge bg-primary">{{ listing.quantity }} {{ listing.unit }}</span>
                    <span class="fw-bold">
                        {% if listing.price == 0 %}
                        Free (Donation)
                        {% else %}
                        ${{ listing.price }}
                        {% endif %}
                    </span>
                </div>
            </div>
            <div class="card-footer bg-white border-top-0">
                <form action="{% url 'cart_add' listing.id %}" method="post">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-success w-100">Add to Cart</button>
                </form>
            </div>
        </div>
    </div>
    {% empty %}
    <div class="col-12 text-center">
        <p>No listings found matching your criteria.</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

with open('templates/home_new.html', 'w') as f:
    f.write(content)
