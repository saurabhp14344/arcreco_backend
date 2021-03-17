from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserUploadFileSerializer, MatchFilesSerializer
from .models import UploadFiles
import pandas as pd
import numpy as np
from core.permissions import UpdateOwnProfile
import json


class UserUploadFileApiView(generics.CreateAPIView, generics.ListAPIView):
    """Create user address"""
    permission_classes = (IsAuthenticated, UpdateOwnProfile)
    queryset = UploadFiles.objects.all()
    serializer_class = UserUploadFileSerializer

    def get_queryset(self):
        return self.queryset.filter(user_profile=self.request.user)

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
                if UploadFiles.objects.filter(user_profile_id=request.user.id).filter(name=serializer.validated_data['name']).first() is None:
                    serializer.save(user_profile=self.request.user)
                    return Response({'status': 'success',
                                     'message': "File upload successfully."
                                     }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'status': 'failed',
                        'message': "File exist.Please choose different file."
                    })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MatchFilesApiView(generics.ListAPIView):
    """get report matched data"""
    permission_classes = (IsAuthenticated,)
    queryset = UploadFiles.objects.all()
    serializer_class = MatchFilesSerializer

    def post(self, request):
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
                ['Creation Date_x', 'Paytm Order ID', 'Order Id', 'Customer Name', 'Total Amount_x',
                 '_merge']].copy()
            csv2 = csv2.rename(
                columns={'Creation Date_x': 'CreationDate', 'Paytm Order ID': 'PaytmOrderId', 'Order Id': 'OrderId', 'Customer Name': 'CustomerName', 'Total Amount_x': 'TotalAmount', '_merge': 'Status'})
            csv2["Status"].replace({"left_only": "unmatched", "both": "matched", "right_only": "unmatched"},
                                   inplace=True)
            csv2 = csv2.groupby('Status', as_index=False)
            matched_count = csv2.size()['matched']
            unmatched_count = csv2.size()['unmatched']
            file1_count = len(file_1_df.index)+1
            file2_count = len(file_2_df.index)
            emp_d = {}
            for df_group_name, df_group in csv2:
                df_group = df_group.drop(columns=['Status'])
                emp_d[df_group_name] = json.loads(df_group.to_json(orient='records'))
            return Response({'status': 'success', 'data': emp_d, 'matched_count': matched_count, 'unmatched_count': unmatched_count, 'file1_count': file1_count, 'file2_count': file2_count })
            # csv2.to_csv('filename_here.csv', index=False)
        return Response({'status': 'failed'})


class TotalFilesApiView(APIView):
    """count uploaded documents"""
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user_count = UploadFiles.objects.filter(user_profile=self.request.user).count()
        content = {'file_count': user_count}
        return Response(content)