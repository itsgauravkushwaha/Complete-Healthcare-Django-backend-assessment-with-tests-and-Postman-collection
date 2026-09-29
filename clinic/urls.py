from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import DoctorViewSet, MappingDetailView, MappingListCreateView, PatientViewSet

router = SimpleRouter()
router.register("patients", PatientViewSet, basename="patients")
router.register("doctors", DoctorViewSet, basename="doctors")

urlpatterns = [
    path("mappings/", MappingListCreateView.as_view(), name="mapping-list-create"),
    path("mappings/<int:pk>/", MappingDetailView.as_view(), name="mapping-detail"),
    path("", include(router.urls)),
]
