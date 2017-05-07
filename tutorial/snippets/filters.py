import django_filters
from models import Town
class ProductFilter(django_filters.FilterSet):
    # min_price = django_filters.NumberFilter(name="price", lookup_type='gte')
    # max_price = django_filters.NumberFilter(name="price", lookup_type='lte')
    class Meta:
        model = Product
        fields = ['county', 'state', 'n_days']