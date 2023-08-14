from .models import Cart,CartItem
from .views import _cart_id
# def counter(request):
#     item_count = 0
    
#     if 'admin' in request.path:
#         return {}
#     else:
#         try:
#             cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
#             if cart:
#                 cart_items = CartItem.objects.filter(cart=cart)
#                 for cart_item in cart_items:
#                     item_count += cart_item.quantity
#         except Cart.DoesNotExist:
#             item_count = 0
    
#     return {'item_count': item_count}

def counter(request):
    if 'carts/carts' in request.path or '' in request.path:
        try:
            cart_count = 0
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                cart_count = 0
                cart = Cart.objects.filter(cart_id=_cart_id(request)).first()  # Use .first() instead of .filter()
                if cart:
                    cart_items = CartItem.objects.filter(cart=cart)
                else:
                    cart_items = []
            
            for cart_item in cart_items:
                cart_count += cart_item.quantity
            
            return {'cart_count': cart_count}
        except Cart.DoesNotExist:
            cart_count = 0
    else:
        return {}
