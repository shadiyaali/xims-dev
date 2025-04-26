
from django.urls import path
from  .views import *

urlpatterns = [
    
    path('policy/', PolicyEnvCreateView.as_view(), name='documentation-create'), 
    path('policy/<int:company_id>/', PolicyEnvAllList.as_view(), name='documentation-detail'), 
    path('policy/<int:pk>/update/', PolicyEnvDeleteView.as_view(), name='policy-env-delete'),
 
    
    path('manuals/', ManualView.as_view(), name='manual-list-create'),
    path('manuals/<int:company_id>/', ManualAllList.as_view(), name='manual-list'),
    # path('manuals/<int:pk>/', ManualDetailView.as_view(), name='manual-detail'),
    # path('manuals-create/', ManualCreateView.as_view(), name='manual-list-create'),
 
]


