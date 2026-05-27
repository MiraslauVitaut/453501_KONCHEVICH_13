from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from properties.models import Property, Deal, Client
from django.db.models import Count, Sum, Avg


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_properties(request):
    qs = Property.objects.filter(is_published=True).values(
        'id', 'title', 'price', 'area', 'city', 'status', 'transaction_type', 'category__name'
    )
    return Response(list(qs))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_property_detail(request, pk):
    try:
        prop = Property.objects.get(pk=pk, is_published=True)
    except Property.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    data = {
        'id': prop.pk,
        'title': prop.title,
        'price': str(prop.price),
        'area': prop.area,
        'city': prop.city,
        'address': prop.address,
        'status': prop.status,
        'description': prop.description,
        'category': prop.category.name,
        'created_at': prop.created_at.strftime('%d/%m/%Y'),
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def api_statistics(request):
    data = {
        'total_properties': Property.objects.count(),
        'available': Property.objects.filter(status='available').count(),
        'total_deals': Deal.objects.count(),
        'completed_deals': Deal.objects.filter(status='completed').count(),
        'total_clients': Client.objects.count(),
        'total_revenue': str(Deal.objects.filter(status='completed').aggregate(s=Sum('amount'))['s'] or 0),
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_deals(request):
    user = request.user
    if user.is_client():
        try:
            client = user.client_profile
            deals = Deal.objects.filter(client=client).values(
                'id', 'property__title', 'deal_type', 'status', 'amount', 'contract_date'
            )
            return Response(list(deals))
        except Exception:
            return Response([])
    elif user.is_employee() or user.is_staff:
        try:
            emp = user.employee_profile
            deals = Deal.objects.filter(agent=emp).values(
                'id', 'property__title', 'client__last_name', 'deal_type', 'status', 'amount', 'contract_date'
            )
            return Response(list(deals))
        except Exception:
            return Response([])
    return Response({'error': 'Forbidden'}, status=403)
