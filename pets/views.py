from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.db.models import Q

from .forms import CustomLoginForm, CustomUserRegisterForm, DoctorClearanceRequestForm
from .models import Profile, Pet, Message, Feedback, BuyerRequest, SellerRequest, DoctorClearanceRequest



# LOGIN VIEW
def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        remember_me = request.POST.get('remember_me')  # Get checkbox value

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role_selected = form.cleaned_data['role']

            user = authenticate(request, username=username, password=password)

            if user:
                if not user.is_active:
                    messages.error(request, "Your account is inactive.")
                elif hasattr(user, 'profile'):
                    role = user.profile.role

                    if role != role_selected:
                        messages.error(request, f"You are not registered as a {role_selected}.")
                    else:
                        login(request, user)

                        # Handle session expiry
                        if remember_me != 'on':
                            request.session.set_expiry(0)  # Session ends when browser closes
                        else:
                            request.session.set_expiry(1209600)  # 2 weeks

                        messages.success(request, 'Successfully logged in!')

                        if role == 'admin':
                            return redirect('admin_home')
                        elif role == 'doctor':
                            return redirect('doctor_home')
                        elif role == 'user':
                            return redirect('user_home')
                        else:
                            messages.error(request, "Invalid role detected.")
                else:
                    messages.error(request, "User profile not found.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})

# REGISTER VIEW
def register_view(request):
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                user = form.save(commit=False)
                role = form.cleaned_data['role'].lower()
                user.save()

                # Create user profile with role
                Profile.objects.create(user=user, role=role)
                messages.success(request, f'{role.capitalize()} registration successful. Please log in.')
                return redirect('login')
    else:
        form = CustomUserRegisterForm()

    return render(request, 'register.html', {'form': form})
# STATIC PAGES

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def footer(request):
    return render(request, 'footer.html')

@login_required
def admin_dashboard(request):
    return render(request, 'admin_home.html')

# USER DASHBOARD

@login_required(login_url='login')
def user_home(request):
    pets = Pet.objects.filter(is_approved=True).order_by('-id')[:6]
    return render(request, 'user_home.html', {'pets': pets})

# DOCTOR DASHBOARD

@login_required(login_url='login')
def doctor_dashboard(request):
    # Check if the user has the 'doctor' role
    if request.user.profile.role == 'doctor':
        # You can add any doctor-specific content here
        doctor = request.user
        # Example: You can display some doctor-related data (e.g., their patients or clearance requests)
        context = {
            'doctor': doctor,
            # Add any other context here if needed
        }
        return render(request, 'doctor_home.html', context)
    else:
        # Redirect or show error if user is not a doctor
        return redirect('login')

# PASSWORD RESET

class CustomPasswordResetView(PasswordResetView):
    template_name = 'forgot_password.html'
    email_template_name = 'password_reset_email.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        messages.success(self.request, 'Password reset instructions sent to your email.')
        return super().form_valid(form)

# PET DETAIL VIEW WITH INLINE CHAT


def pet_detail(request, pet_id):
    # Get the pet object
    pet = get_object_or_404(Pet, id=pet_id)
    
    # Get the first DoctorClearanceRequest related to the logged-in user and the pet
    doctor_request = DoctorClearanceRequest.objects.filter(pet=pet, requested_by=request.user).first()
    
    return render(request, 'pet_details.html', {
        'pet': pet,
        'doctor_request': doctor_request,  # Pass the doctor request to the template
    })
# Redirect to specific chatroom

@login_required(login_url='login')
def create_or_redirect_chat(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    seller = pet.owner
    buyer = request.user

    if buyer == seller:
        messages.info(request, "You are the seller of this pet.")
        return redirect('pet_detail', pet_id=pet.id)

    return redirect('chatroom', pet_id=pet.id, other_user_id=seller.id)

# CHATROOM VIEW

@login_required(login_url='login')
def chatroom(request, pet_id, other_user_id):
    pet = get_object_or_404(Pet, id=pet_id)
    other = get_object_or_404(User, id=other_user_id)
    user = request.user

    # Allow only the pet's buyer and seller to chat
    if user != pet.owner and other != pet.owner:
        messages.error(request, "Access Denied.")
        return redirect('user_home')

    if user == other:
        messages.error(request, "You cannot chat with yourself.")
        return redirect('pet_detail', pet_id=pet.id)

    messages_qs = Message.objects.filter(
        pet=pet
    ).filter(
        Q(sender=user, receiver=other) | Q(sender=other, receiver=user)
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            Message.objects.create(
                pet=pet,
                sender=user,
                receiver=other,
                content=content
            )
        return redirect('chatroom', pet_id=pet.id, other_user_id=other.id)

    return render(request, 'chatroom.html', {
        'pet': pet,
        'other_user': other,
        'messages': messages_qs
    })

# DELETE A CHAT MESSAGE

@login_required(login_url='login')
def delete_message(request, message_id):
    msg = get_object_or_404(Message, id=message_id)
    if msg.sender == request.user:
        msg.delete()
    return redirect('chatroom', pet_id=msg.pet.id, other_user_id=msg.receiver.id)

# SELLER CHAT LIST

@login_required(login_url='login')
def seller_chat_list(request):
    seller = request.user
    pets = Pet.objects.filter(seller=seller)
    messages = Message.objects.filter(pet__in=pets)

    chatrooms = {}
    for msg in messages:
        pet = msg.pet
        buyer = msg.receiver if msg.sender == seller else msg.sender
        key = (pet.id, buyer.id)
        if key not in chatrooms:
            chatrooms[key] = {
                'pet': pet,
                'buyer': buyer
            }

    return render(request, 'seller_chat_list.html', {
        'chatrooms': chatrooms.values()
    })

@login_required(login_url='login')
def seller_home(request):
    return render(request, 'seller_home.html')

# ADD PETS

@login_required(login_url='login')
def add_pets(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        pet_type = request.POST.get('pet_type')
        breed = request.POST.get('breed')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        pet = Pet.objects.create(
            name=name,
            pet_type=pet_type,
            breed=breed,
            age=age,
            gender=gender,
            description=description,
            owner=request.user,
            seller=request.user,
            image=image,
            is_approved=False
        )
        return redirect('view_my_pets')
    return render(request, 'add_pets.html')

# VIEW SELLER'S PETS

@login_required(login_url='login')
def view_my_pets(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'view_my_pets.html', {'pets': pets})

# FEEDBACK FORM DISPLAY
@login_required(login_url='login')
def feedback(request):
    return render(request, 'feedback.html')

# FEEDBACK SUBMISSION
@login_required(login_url='login')
def submit_feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        feedback = Feedback(name=name, email=email, message=message)
        feedback.save()
        return redirect('thank_you')
    return redirect('feedback')

# THANK YOU PAGE
@login_required(login_url='login')
def thank_you(request):
    return render(request, 'thank_you.html')

# SELLER REQUESTS
@login_required(login_url='login')
def seller_request(request):
    seller_requests = SellerRequest.objects.all()
    return render(request, 'seller_requests.html', {
        'seller_requests': seller_requests,
    })
@login_required(login_url='login')
def view_seller_request(request, request_id):
    seller_request = get_object_or_404(SellerRequest, id=request_id)
    return render(request, 'view_seller_request.html', {
        'seller_requests': seller_request,
    })

# BUYER REQUEST VIEW
@login_required
def buyer_request_view(request):
    requests = DoctorClearanceRequest.objects.all().order_by('-created_at')
    return render(request, 'buyer_request.html', {'requests': requests})
    

@login_required(login_url='login')
def update_request_status(request, request_id, status):
    buyer_request = BuyerRequest.objects.get(id=request_id, pet__seller=request.user)
    if status in ['Approved', 'Rejected']:
        buyer_request.status = status
        buyer_request.save()
    return redirect('buyer_request')

# MY REQUEST VIEW
from .models import AdoptionRequest  # Assuming your model is named AdoptionRequest



@login_required
def request_doctor_clearance(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    existing_request = DoctorClearanceRequest.objects.filter(pet=pet, requested_by=request.user).first()

    if not existing_request:
        DoctorClearanceRequest.objects.create(pet=pet, requested_by=request.user)
    
    return redirect('pet_detail', pet_id=pet.id)

@login_required
def my_requests(request):
    requests = DoctorClearanceRequest.objects.filter(requested_by=request.user).order_by('-created_at')
    return render(request, 'my_requests.html', {'requests': requests})


@login_required(login_url='login')# View to manage all user profiles
def manage_users(request):
    profiles = Profile.objects.select_related('user').all()
    return render(request, 'manage_users.html', {'profiles': profiles})

@login_required(login_url='login')
def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()

    profile = getattr(user, 'profile', None)
    if profile:
        profile.status = 'active'
        profile.save()

    messages.success(request, f"{user.username} is now Active!")
    return redirect('manage_users')

@login_required(login_url='login')
def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()

    profile = getattr(user, 'profile', None)
    if profile:
        profile.status = 'inactive'
        profile.save()

    messages.success(request, f"{user.username} is now Inactive!")
    return redirect('manage_users')

@login_required(login_url='login')
def view_pets(request):
    pets = Pet.objects.filter(is_approved=True)
    return render(request, 'viewpets.html', {'pets': pets})


@login_required(login_url='login')
def update_pet_status(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            pet.is_approved = True
            messages.success(request, f"Pet '{pet.name}' has been approved.")
        elif action == 'reject':
            pet.is_approved = False
            messages.warning(request, f"Pet '{pet.name}' has been rejected.")
        pet.save()
    return redirect('viewpets')  # Replace with your view name for showing the pet list




@login_required(login_url='login')
def approve_pets(request):
    pets = Pet.objects.filter(is_approved=False)
    return render(request, 'approvepets.html', {'pets': pets})

@login_required(login_url='login')
def approve_pet(request, pet_id):
    if request.method == 'POST':
        pet = get_object_or_404(Pet, id=pet_id)
        pet.is_approved = True
        pet.save()
        messages.success(request, f"{pet.name} has been approved.")
    return redirect('approve_pets')

@login_required(login_url='login')
def reject_pet(request, pet_id):
    if request.method == 'POST':
        pet = get_object_or_404(Pet, id=pet_id)
        pet_name = pet.name
        pet.delete()
        messages.warning(request, f"{pet_name} has been rejected and removed.")
    return redirect('approve_pets')

from django.contrib.auth.hashers import make_password
from .forms import AddDoctorForm


@login_required(login_url='login')
def add_doctor(request):
    if request.method == 'POST':
        form = AddDoctorForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            else:
                # Create the User object
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password)
                )

                # Create the Profile linked to this User
                profile = form.save(commit=False)
                profile.user = user
                profile.role = 'doctor'
                profile.save()

                messages.success(request, "Doctor added successfully.")
                return redirect('view_doctors')
    else:
        form = AddDoctorForm()

    return render(request, 'adddoctor.html', {'form': form})


@login_required(login_url='login')
def view_doctors(request):
    # If using Profile model to get doctors
    doctors = Profile.objects.filter(role='doctor')

    # If using Doctor model for detailed doctor info
    # doctors = Doctor.objects.all()

    return render(request, 'view_doctor.html', {'doctors': doctors})



@login_required(login_url='login')
def edit_doctor(request, id):
    doctor = get_object_or_404(Profile, id=id)
    if request.method == 'POST':
        form = AddDoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor updated successfully.')
            return redirect('view_doctors')
    else:
        form = AddDoctorForm(instance=doctor)
    return render(request, 'edit_doctor.html', {'form': form})

@login_required(login_url='login')
def delete_doctor(request, id):
    doctor = get_object_or_404(Profile, id=id)
    doctor.delete()
    messages.success(request, 'Doctor deleted successfully.')
    return redirect('view_doctors')


def view_feedback(request):
    feedbacks = Feedback.objects.all()  # Retrieve all feedback entries
    return render(request, 'view_feedback.html', {'feedbacks':feedbacks})



# views.py
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .models import Contact

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save message to the database
            Contact.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )

            # Send confirmation email to the user
            send_mail(
                'Thank you for contacting us!',
                'We have received your message and will get back to you soon.',
                settings.DEFAULT_FROM_EMAIL,
                [form.cleaned_data['email']],
                fail_silently=False,
            )

            # Optionally, send an email to admin/support team
            send_mail(
                'New Contact Us Message',
                f"Message from {form.cleaned_data['name']} ({form.cleaned_data['email']}):\n\n{form.cleaned_data['message']}",
                settings.DEFAULT_FROM_EMAIL,
                ['support@adoptapaw.com'],
                fail_silently=False,
            )

            # Redirect to the home page after successful submission
            return redirect('home')  # or any other page you'd like to redirect to
    else:
        form = ContactForm()

    return render(request, 'contactus.html', {'form': form})
                                                  
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings

# Temporary token store
reset_tokens = {}

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            token = get_random_string(50)
            reset_tokens[token] = user.username
            reset_link = request.build_absolute_uri(f"/reset-password/{token}/")
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            return render(request, 'forgot_password.html', {'message': 'Reset link sent to your email!'})
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'Email not registered'})
    return render(request, 'forgot_password.html')


def reset_password(request, token):
    if token not in reset_tokens:
        return render(request, 'reset_password.html', {'error': 'Invalid or expired token'})

    if request.method == 'POST':
        password = request.POST['password']
        username = reset_tokens[token]
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        del reset_tokens[token]
        return render(request, 'reset_password.html', {'message': 'Password reset successfully'})
    
    return render(request, 'reset_password.html')                                                  

# views.py


@login_required
def mark_as_adopted(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, seller=request.user)  # Only allow the seller to update
    if request.method == 'POST':
        pet.is_adopted = True  # Mark the pet as adopted
        pet.save()  # Save the changes to the database
    return redirect('view_my_pets')  # Redirect back to the 'View My Pets' page

from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})