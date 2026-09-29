from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Doctor, Patient, PatientDoctorMapping
from .permissions import IsCreatorOrReadOnly
from .serializers import DoctorSerializer, MappingSerializer, PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer

    def get_queryset(self):
        # Listing, detail, updates and deletion all use the same ownership filter.
        return Patient.objects.filter(created_by=self.request.user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all().order_by("id")
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = MappingSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor").order_by("id")


class MappingDetailView(APIView):
    """GET pk = patient ID; DELETE pk = mapping ID (as assignment specifies)."""

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related("doctor")
        return Response([
            {"mapping_id": mapping.id, "doctor": DoctorSerializer(mapping.doctor).data}
            for mapping in mappings
        ])

    def delete(self, request, pk):
        mapping = get_object_or_404(
            PatientDoctorMapping, pk=pk, patient__created_by=request.user
        )
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
