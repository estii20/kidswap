from django.shortcuts import render, redirect
from .models import ClothingItem, ItemImage, Notification
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ClothingItemForm
from .models import CartItem
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .utils import notify_user


def home(request):
    query = request.GET.get('q')
    size = request.GET.get('size')
    category = request.GET.get('category')

    items = ClothingItem.objects.filter(sold=False).order_by('-posted_at')

    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if size:
        items = items.filter(size__iexact=size)
    if category:
        items = items.filter(category=category)

    featured_products = ClothingItem.objects.filter(is_featured=True, sold=False).order_by('-posted_at')[:8]

    return render(request, 'marketplace/home.html', {
        'items': items,
        'query': query,
        'size': size,
        'category': category,
        'featured_products': featured_products,
    })


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created. You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'marketplace/register.html', {'form': form})


@login_required
def add_item(request):
    if request.method == 'POST':
        form = ClothingItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return redirect('home')
    else:
        form = ClothingItemForm()
    return render(request, 'marketplace/add_item.html', {'form': form})


@login_required
def add_to_cart(request, item_id):
    item = ClothingItem.objects.get(id=item_id)
    CartItem.objects.get_or_create(user=request.user, item=item)
    if item.seller == request.user:
            messages.error(request, "You can't add your own item to your cart.")
            return redirect('home')
    else:
        return redirect('view_cart')


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.item.price for item in cart_items)
    return render(request, 'marketplace/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def remove_from_cart(request, item_id):
    CartItem.objects.filter(user=request.user, item_id=item_id).delete()
    return redirect('view_cart')


@login_required
@csrf_exempt
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    # Here is where you'd integrate Stripe
    # For now, simulate a successful checkout:
    for cart_item in cart_items:
        item = cart_item.item
        item.sold = True
        item.save()

        # Notify seller
        notify_user(item.seller, f"Your item '{item.title}' has been sold!")

        # Notify buyer (current user)
        notify_user(request.user, f"You bought '{item.title}' successfully!")

        cart_item.delete()

    return render(request, 'marketplace/checkout_success.html')


@login_required
def profile(request):
    listed_items = ClothingItem.objects.filter(seller=request.user).order_by('-posted_at')
    sold_items = listed_items.filter(sold=True)
    unsold_items = listed_items.filter(sold=False)

    purchased_items = ClothingItem.objects.filter(
        sold=True,
        cartitem__user=request.user
    ).distinct()  # If you want to show what they bought

    return render(request, 'marketplace/profile.html', {
        'unsold_items': unsold_items,
        'sold_items': sold_items,
        'purchased_items': purchased_items,
    })


@login_required
def add_item(request):
    if request.method == 'POST':
        form = ClothingItemForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')

        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()

            for image in images:
                ItemImage.objects.create(item=item, image=image)

            return redirect('home')
    else:
        form = ClothingItemForm()
    return render(request, 'marketplace/add_item.html', {'form': form})


def item_detail(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)
    return render(request, 'marketplace/item_detail.html', {'item': item})


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)

    if item.seller != request.user:
        return HttpResponseForbidden("You are not allowed to edit this item.")

    if request.method == 'POST':
        form = ClothingItemForm(request.POST, request.FILES, instance=item)
        images = request.FILES.getlist('images')
        if form.is_valid():
            form.save()
            # Add new images if uploaded
            for image in images:
                ItemImage.objects.create(item=item, image=image)
            messages.success(request, "Item updated successfully.")
            return redirect('item_detail', item_id=item.id)
    else:
        form = ClothingItemForm(instance=item)

    return render(request, 'marketplace/edit_item.html', {'form': form, 'item': item})


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)

    if item.seller != request.user:
        return HttpResponseForbidden("You are not allowed to delete this item.")

    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('profile')

    return render(request, 'marketplace/delete_item.html', {'item': item})


@login_required
def mark_notification_read(request, notification_id):
    note = get_object_or_404(Notification, id=notification_id, user=request.user)
    note.is_read = True
    note.save()
    return redirect('profile')
