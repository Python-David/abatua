from django.contrib import admin

from .models import Product, Variation, ReviewRating


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("product_name",)}
    list_display = (
        "product_name",
        "price",
        "slug",
        "category",
        "date_modified",
        "is_available",
    )

class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "subject",
        "rating",
        "status",
        "created_at",
        "updated_at",
    )


class VariationAdmin(admin.ModelAdmin):
    readonly_fields = ("date_created",)
    list_display = ("product", "variation_category", "variation_value", "is_active")
    list_editable = ("is_active",)
    list_filter = (
        "product",
        "variation_category",
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)
