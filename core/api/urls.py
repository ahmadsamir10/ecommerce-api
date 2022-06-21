from django.urls import path
from rest_framework import routers
from .views import (
                        HomeView,
                        ListRetrieveCategoryView,
                        ListCityByCountryView,
                        ListCountryView,
                        ListSubcategoryByCategoryView,
                        ListProductsView,
                        RetrieveProductView,
                        RetrieveSubCategoryView,
                        ProductSerachView,
                        ProductFilterView,
                        ListBrandsView,
                        ListOffersView
                        

                    )

app_name = 'core'

router = routers.SimpleRouter()
router.register('categories', ListRetrieveCategoryView, 'categories')




urlpatterns = [
    
    path('home', HomeView.as_view(), name='home'),
    path('subcategory/<pk>', RetrieveSubCategoryView.as_view(), name='subcategory'),
    path('categories/<pk>/subcategories', ListSubcategoryByCategoryView.as_view(), name='list-subcategories-by-category'),
    path('products', ListProductsView.as_view(), name='list-products'),
    path('products/<pk>', RetrieveProductView.as_view(), name='retrieve-product'),
    path('countries', ListCountryView.as_view(), name='countries'),
    path('cities/<pk>', ListCityByCountryView.as_view(), name='list-cities-by-country'),
    path('brands', ListBrandsView.as_view(), name='brands'),
    path('product-search', ProductSerachView.as_view(), name='product-search'),
    path('product-filter', ProductFilterView.as_view(), name='product-filter'),
    path('offers', ListOffersView.as_view(), name='offers'),
    
]

urlpatterns += router.urls