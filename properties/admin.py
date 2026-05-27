from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PropertyCategory, Employee, Owner, Client, Property, PropertyTag,
    PropertyImage, Deal, Article, CompanyInfo, GlossaryTerm, Review,
    Vacancy, PromoCode
)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'caption', 'is_main']


@admin.register(PropertyCategory)
class PropertyCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'department', 'hire_date', 'salary', 'is_active']
    list_filter = ['is_active', 'department', 'position']
    search_fields = ['user__first_name', 'user__last_name', 'position']
    list_editable = ['is_active']

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'ФИО'


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'address', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'address', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    list_filter = ['created_at']


@admin.register(PropertyTag)
class PropertyTagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'transaction_type', 'status', 'price', 'area', 'city', 'agent', 'is_published', 'created_at']
    list_filter = ['status', 'transaction_type', 'category', 'city', 'is_published']
    search_fields = ['title', 'address', 'city', 'description']
    list_editable = ['status', 'is_published']
    filter_horizontal = ['tags']
    inlines = [PropertyImageInline]
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Основное', {'fields': ('title', 'category', 'owner', 'agent', 'transaction_type', 'status', 'is_published')}),
        ('Характеристики', {'fields': ('price', 'area', 'rooms', 'floor', 'total_floors', 'year_built')}),
        ('Адрес', {'fields': ('address', 'city', 'district')}),
        ('Описание', {'fields': ('description', 'tags')}),
        ('Статистика', {'fields': ('views_count', 'created_at', 'updated_at')}),
    )


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['id', 'property', 'client', 'agent', 'deal_type', 'status', 'amount', 'commission', 'contract_date']
    list_filter = ['status', 'deal_type', 'contract_date']
    search_fields = ['property__title', 'client__last_name', 'client__first_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'contract_date'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at']
    list_editable = ['is_published']
    search_fields = ['title', 'content']


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'founded_year']


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ['term', 'created_at']
    search_fields = ['term', 'definition']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_approved', 'created_at']
    list_editable = ['is_approved']
    list_filter = ['rating', 'is_approved']


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'salary_from', 'salary_to', 'is_active', 'created_at']
    list_editable = ['is_active']


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'valid_from', 'valid_to', 'is_active']
    list_editable = ['is_active']
    list_filter = ['is_active']
