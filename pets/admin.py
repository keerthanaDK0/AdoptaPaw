from django.contrib import admin
from .models import Profile, Pet, Feedback
from django.contrib.auth.models import User

# Register Profile model with the admin interface
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status')  # Display user, role, and status in list
    search_fields = ('user__username', 'role', 'status')  # Enable search by user, role, or status
    list_filter = ('role', 'status')  # Add filter by role and status

    # Display the user as 'No user assigned' if it's null
    def user_display(self, obj):
        return obj.user.username if obj.user else 'No user assigned'
    
    user_display.short_description = 'User'

admin.site.register(Profile, ProfileAdmin)





# Register Pet model with the admin interface
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'pet_type', 'breed', 'age', 'owner', 'is_approved')  # Display pet details
    search_fields = ('name', 'breed', 'owner__username')  # Enable search by pet name, breed, and owner
    list_filter = ('pet_type', 'is_approved')  # Add filter by pet type and approval status

admin.site.register(Pet, PetAdmin)



class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message')  # Fields to display in the list view
    search_fields = ('name', 'email', 'message')  # Enable search functionality

admin.site.register(Feedback, FeedbackAdmin)




from django.contrib import admin
from .models import Product

admin.site.register(Product)

