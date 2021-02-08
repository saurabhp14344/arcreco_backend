from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserUploadFileSerializer, MatchFilesSerializer
from .models import UploadFiles
import pandas as pd
import numpy as np


class UserUploadFileApiView(generics.CreateAPIView, generics.ListAPIView):
    """Create user address"""
    permission_classes = (IsAuthenticated,)
    queryset = UploadFiles.objects.all()
    serializer_class = UserUploadFileSerializer

    def post(self, request, *args, **kwargs):
        """Set the user profile address"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            filename = serializer.validated_data['file']
            data_name = request.data.get('file').name
            uploaded = data_name.split('.')
            serializer.validated_data['name'] = uploaded[0]
            df = pd.read_excel(filename, engine='openpyxl')
            if df.empty is False:
                if UploadFiles.objects.filter(name=serializer.validated_data['name']).first() is None:
                    serializer.save(user_profile=self.request.user)
                    return Response({'status': 'success',
                                     'message': "file upload successfully."
                                     }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'status': 'failed',
                        'message': "file name already exist."
                    })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MatchFilesApiView(generics.ListAPIView):
    """get report matched data"""
    permission_classes = (IsAuthenticated,)
    queryset = UploadFiles.objects.all()
    serializer_class = MatchFilesSerializer

    def get(self, request, *args, **kwargs):
        """get the user file matched data"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file_1_df = pd.read_excel(serializer.validated_data['file1'], engine='openpyxl')
            col_range = list(np.arange(0, 19, 1))
            col_range = col_range[:2] + col_range[3:]
            file_2_df = pd.read_excel(serializer.validated_data['file2'], usecols=col_range, engine='openpyxl')
            file_2_df = file_2_df.dropna()
            final_df = pd.merge(file_1_df, file_2_df, on=['Order Id', 'Paytm Order ID'], how='outer',
                                indicator=True)
            csv2 = final_df[
                ['Creation Date_x', 'Paytm Order ID', 'Order Id', 'Customer Name', 'Email', 'Total Amount_x',
                 '_merge']].copy()
            csv2 = csv2.rename(
                columns={'Creation Date_x': 'Creation Date', 'Total Amount_x': 'Total Amount', '_merge': 'Status'})
            csv2["Status"].replace({"left_only": "Unmatched", "both": "matched", "right_only": "Unmatched"},
                                   inplace=True)
            data_json = csv2.to_json(orient='index')

            return Response({'status': 'success', 'data': data_json})
            # csv2.to_csv('filename_here.csv', index=False)
        return Response({'status': 'failed'})