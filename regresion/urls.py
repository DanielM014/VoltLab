from django.urls import path
from .views import ComparacionModeloView
from regresion.views import PrediccionConsumoView

urlpatterns = [
    path("comparacion/", ComparacionModeloView.as_view(), name="comparacion-modelo"),
    path('prediccion/', PrediccionConsumoView.as_view(), name='prediccion-consumo'),
]
