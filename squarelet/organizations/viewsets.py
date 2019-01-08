# Third Party
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_402_PAYMENT_REQUIRED

# Squarelet
from squarelet.oidc.permissions import ScopePermission
from squarelet.organizations.exceptions import InsufficientRequestsError

# Local
from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all().select_related("plan")
    serializer_class = OrganizationSerializer
    permission_classes = (ScopePermission,)
    read_scopes = ("read_organization",)
    write_scopes = ("write_organization",)


class OrganizationRequestsViewSet(viewsets.ViewSet):
    """Viewset for managing the requests of an organization"""

    # XXX this should go away

    permission_classes = (ScopePermission,)
    write_scopes = ("write_requests",)

    # XXX make this a "create" only view

    def create(self, request, organization_pk=None):
        organization = Organization.objects.get(pk=organization_pk)
        if "amount" in request.data:
            try:
                request_count = organization.make_requests(int(request.data["amount"]))
            except InsufficientRequestsError as exc:
                return Response(
                    {"extra": exc.args[0]}, status=HTTP_402_PAYMENT_REQUIRED
                )
            else:
                return Response(request_count)
        elif "return_regular" in request.data and "return_monthly" in request.data:
            # XXX check int(v) for error
            organization.return_requests({k: int(v) for k, v in request.data.items()})
            return Response("OK")
        else:
            return Response("Error", status=HTTP_400_BAD_REQUEST)
