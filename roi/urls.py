from django.urls import path
from .views import ROIRealView

urlpatterns = [
    path('real/', ROIRealView.as_view(), name='roi-real'),
]