from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from .models import Account, UserProfile, NewsletterSubscriber
from .forms import RegistrationForm, UserForm, UserProfileForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import re
from django.contrib.auth import login
from django.urls import reverse
from django.db.utils import IntegrityError
# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            username = email.split("@")[0]
            password = form.cleaned_data["password"]
            phone_number = form.cleaned_data["phone_number"]
            newsletter_subscription = form.cleaned_data['newsletter_subscription']
            error_messages = []
            if (
                password == first_name
                or password == last_name
                or first_name in password
                or last_name in password
            ):
                error_messages.append("Password cannot be the same as your first name or last name.")

            if not re.search(r"\d", password):
                error_messages.append("Password must contain at least one digit.")

            if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\"|,.<>\/?]", password):
                error_messages.append("Password must contain at least one special character (!@#$%^&*()_-+=[]{};:'\"|,.<>/?).")

            if not re.search(r"[A-Z]", password):
                error_messages.append("Password must contain at least one uppercase letter.")

            if not re.search(r"[a-z]", password):
                error_messages.append("Password must contain at least one lowercase letter.")

            if error_messages:
                messages.error(request, "Invalid password. Please correct the errors.")
                form.add_error('password', error_messages)
                form.fields['password'].widget.attrs['class'] 
                return render(request, "accounts/register.html", {"form": form})

            try:
                user = Account.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password,
                    newsletter_subscription=newsletter_subscription,
                )
                user.phone_number = phone_number
                user.is_active = False
                user.save()
                messages.success(
                    request,
                    "Registration successful .. We have sent you an email to verify your account",
                )
            except IntegrityError:
                messages.error(request, "This email is already registered. Please use a different email.")
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"http://{current_site}{reverse('newtab', kwargs={'uidb64': uid, 'token': token})}"
            
            mail_subject = "Please activate your account"
            message = render_to_string(
                "accounts/newtab.html",
                {
                    "user": user,
                    "activation_link": activation_link,
                },
            )
            to_email = email

            # Create email message with HTML content
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            email_message.attach_alternative(message, "text/html")

            # Send email
            email_message.send()
            return redirect("user_login")
    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }

    return render(request, "accounts/register.html", context)

def user_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)

                    # Existing variations in a cart
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # Product variations in a cart
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            return redirect("home")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("user_login")

    return render(request,"accounts/login.html")

def newtab(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    user = Account._default_manager.get(pk=uid)
    current_site = get_current_site(request)
    activation_link = "http://{}/accounts/activate/{}/{}/".format(
        current_site.domain,
        uidb64,
        token,
    )
    context={
        'user':user,
        'activation_link':activation_link
    }
    return render(request,"accounts/accounts_verification_email.html",context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and not user.is_active:  # Check if the user is not already active
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            if user.newsletter_subscription:
                NewsletterSubscriber.objects.create(user=user)
            login(request, user)
            return redirect("home")

    messages.error(request, "Invalid activation link")
    return redirect("register")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out")
    return redirect("user_login")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            send_mail(
                mail_subject,
                message,
                recipient_list=[email],
                from_email="khamaan5@gmail.com",
            )

            messages.success(
                request, "Password reset email has been sent to your email address"
            )
            return redirect("user_login")
        else:
            messages.error(request, "Account does not exist")
            return redirect("forgotPassword")
    return render(request, "accounts/forgotPassword.html")


def reset_password_validate(request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
        if user is not None and default_token_generator.check_token(user, token):
            request.session["uid"] = uid
            messages.success(request, "Please reset your password")
            return redirect("resetPassword")
        else:
            messages.error(request, "This link has been expired")
            return redirect("user_login")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("user_login")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("resetPassword")
    else:
        return render(request, "accounts/resetPassword.html")


@login_required(login_url="user_login")
def dashboard(request):
    User = get_user_model()
    orders = Order.objects.order_by("-current_date").filter(
        user_id=request.user.id, is_ordered=True
    )
    orders_count = orders.count()
    try:
        user = User.objects.get(id=request.user.id)
        try:
            userprofile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            userprofile = UserProfile.objects.create(user=user,profile_picture='userprofile/download.jpeg')
    except User.DoesNotExist:
        user = None
        # userprofile = UserProfile.objects.get(user=request.user.id)
    context = {
        "orders_count": orders_count,
        "userprofile": userprofile,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required(login_url="user_login")
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=userprofile,
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated")
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "userprofile": userprofile,
    }
    return render(request, "accounts/edit_profile.html", context)


def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    context = {
        "orders": orders,
    }
    return render(request, "accounts/my_orders.html", context)


@login_required(login_url="user_login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = Account.objects.get(username=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password updated successfully")
                return redirect("user_login")
            else:
                messages.error(request, "Please enter valid current password")
                return redirect("change_password")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("change_password")
    return render(request, "accounts/change_password.html")