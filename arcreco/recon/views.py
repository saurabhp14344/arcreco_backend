from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserUploadFileSerializer, TotalReconcileSerializer, ReportSerializer
from .models import UploadFiles, TotalReconcile
import pandas as pd
from django.db import connection
from django.db.models import Sum
import numpy as np
from core.permissions import UpdateOwnProfile
import datetime
import timestring
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
                if UploadFiles.objects.filter(user_profile_id=request.user.id).filter(
                        name=serializer.validated_data['name']).first() is None:
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
    serializer_class = TotalReconcileSerializer

    def post(self, request):
        """get the user file matched data"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file_1_df = pd.read_excel(serializer.validated_data['file1'], engine='openpyxl')
            col_range = list(np.arange(0, 19, 1))
            col_range = col_range[:2] + col_range[3:]
            file_2_df = pd.read_excel(serializer.validated_data['file2'], usecols=col_range, engine='openpyxl')
            # file_2_df = file_2_df.dropna()
            rename_file2 = file_2_df.rename(columns={'entity_id': 'TXN ID'})
            ageing = file_1_df['Item Status'].value_counts()
            start_date = file_1_df['Creation Date'].iloc[0]
            end_date = file_1_df['Creation Date'].iloc[-1]
            final_df = pd.merge(file_1_df, rename_file2, on=['TXN ID'], how='left',
                                indicator=True)

            csv2 = final_df[
                ['Order Id', 'Creation Date', 'Customer Detail', 'Total Amount',
                 '_merge']].copy()
            csv2 = csv2.rename(
                columns={'_merge': 'Status'})
            csv2["Status"].replace({"left_only": "unmatched", "both": "matched", "right_only": "unmatched"},
                                   inplace=True)
            csv2 = csv2.groupby('Status', as_index=False)



            emp_d = {}
            for df_group_name, df_group in csv2:
                df_group = df_group.drop(columns=['Status'])
                emp_d[df_group_name] = json.loads(df_group.to_json(orient='records'))

            serializer.create(profile=self.request.user,
                              name=serializer.validated_data['file1'].split('/')[-1],
                              sales_count=len(file_1_df.index),
                              reconcile_count=csv2.size()['matched'],
                              ageing_count=ageing['COD'],
                              start_date=timestring.Date(start_date),
                              end_date=timestring.Date(end_date)
                              )
            return Response({'status': 'success', 'data': emp_d, 'rows_reconciled   ': len(file_1_df.index),
                             'matched_entries': csv2.size()['matched'], 'unmatched_entries': csv2.size()['unmatched']})
            # csv2.to_csv('filename_here.csv', index=False)
        return Response({'status': 'failed'})


class TotalFilesApiView(APIView):
    """count uploaded documents"""
    permission_classes = (IsAuthenticated,)
    total_sales = 0
    total_reconcile = 0
    total_ageing = 0

    def get(self, request, format=None):
        user_count = UploadFiles.objects.filter(user_profile=self.request.user).count()
        sales = TotalReconcile.objects.filter(user_profile=self.request.user).aggregate(Sum('sales_count'))
        reconcile = TotalReconcile.objects.filter(user_profile=self.request.user).aggregate(Sum('reconcile_count'))
        ageing = TotalReconcile.objects.filter(user_profile=self.request.user).aggregate(Sum('ageing_count'))
        all_data = {}
        sub_dict = {}
        day_dict = {}
        if sales['sales_count__sum']:
            self.total_sales = sales['sales_count__sum']
        if reconcile['reconcile_count__sum']:
            self.total_reconcile = reconcile['reconcile_count__sum']
        if ageing['ageing_count__sum']:
            self.total_ageing = ageing['ageing_count__sum']
        content = {
            'total_uploaded_files': user_count,
            'total_sales': self.total_sales,
            'total_reconcile': self.total_reconcile,
            'total_ageing': self.total_ageing,
            'rows_reconciled': 0,
            'matched_entries': 0,
            'unmatched_entries': 0
        }
        all_data['dashboard_data'] = content
        sub_dict['December 2020'] = {
            'total': 2850250.00,
            't': 0.00,
            't+1': 560962.00,
            't+2': 1256083.00,
            't+3': 1033205.00
        }
        sub_dict['January 2021'] = {
            'total': 2650250.00,
            't': 0.00,
            't+1': 460962.00,
            't+2': 1156083.00,
            't+3': 1033205.00
        }
        sub_dict['February 2021'] = {
            'total': 2750250.00,
            't': 0.00,
            't+1': 460962.00,
            't+2': 1156083.00,
            't+3': 1133205.00
        }
        sub_dict['March 2021'] = {
            'total': 2350250.00,
            't': 0.00,
            't+1': 260962.00,
            't+2': 1056083.00,
            't+3': 1033205.00
        }
        sub_dict['April 2021'] = {
            'total': 2950250.00,
            't': 0.00,
            't+1': 560962.00,
            't+2': 1356083.00,
            't+3': 1033205.00
        }
        day_dict['November 2020'] = {
            'Settlement amount': 2450250.00,
            'bank amount': 2450250.00,
            'open amount': 260962.00,
            'outstanding': 0.00,
        }
        day_dict['December 2020'] = {
            'Settlement amount': 2730154.00,
            'bank amount': 2730154.00,
            'open amount': 120096.00,
            'outstanding': 0.00,
        }
        day_dict['January 2021'] = {
            'Settlement amount': 2548155.00,
            'bank amount': 2650250.00,
            'open amount': 102095.00,
            'outstanding': 0.00,
        }
        day_dict['February 2021'] = {
            'Settlement amount': 2459143.00,
            'bank amount': 2459143.00,
            'open amount': 291107.00,
            'outstanding': 0.00,
        }
        day_dict['March 2021'] = {
            'Settlement amount': 2180897.00,
            'bank amount': 2180897.00,
            'open amount': 169353.00,
            'outstanding': 0.00,
        }

        all_data['time_reconcile'] = sub_dict
        all_data['day_reconcile'] = day_dict
        return Response({
                'status': 'success',
                'data': all_data
        })


class AgeingReportApiView(APIView):
    """get ageing reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get COD report files"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file_df = pd.read_excel(serializer.validated_data['file'], engine='openpyxl')
            ageing_csv = file_df[
                ['Order Id', 'Creation Date', 'Customer Detail', 'Mobile', 'Item Status', 'Total Amount']].copy()
            file_ageing = ageing_csv.groupby('Item Status')
            data = {}
            for ageing_group_name, ageing_group in file_ageing:
                ageing_group = ageing_group.drop(columns=['Item Status'])
                if ageing_group_name == 'COD':
                    data['ageing'] = json.loads(ageing_group.to_json(orient='records'))
                    data['ageing'].append({'total_order_amount': round(ageing_group['Total Amount'].sum(), 2)})
            if data:
                return Response({'status': 'success', 'data': data})
        return Response({'status': 'failed', 'data': 'No data found'})


class ModePaymentReportApiView(APIView):
    """get payment mode reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get mode of payment files"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file_df = pd.read_excel(serializer.validated_data['file'], engine='openpyxl')
            payment_mode = file_df[
                ['entity_id', 'payment_method', 'amount', 'fee (exclusive tax)', 'tax', 'debit', 'credit', 'entity_created_at', 'order_id']].copy()
            payment_mode_file = payment_mode.groupby('payment_method')
            data = {}
            for payment_group_name, payment_group in payment_mode_file:
                payment_group = payment_group.drop(columns=['payment_method'])
                data[payment_group_name] = json.loads(payment_group.to_json(orient='records'))
                data[payment_group_name].append({'total_order_amount': round(payment_group['amount'].sum(), 2)})
                data[payment_group_name].append({'total_gateway_fee': round(payment_group['fee (exclusive tax)'].sum(), 2)})
                data[payment_group_name].append({'total_tax_amount': round(payment_group['tax'].sum(), 2)})
                data[payment_group_name].append({'total_debit_amount': round(payment_group['debit'].sum(), 2)})
                data[payment_group_name].append({'total_credit_amount': round(payment_group['credit'].sum(), 2)})
            if data:
                return Response({'status': 'success', 'data': data})
        return Response({'status': 'failed', 'data': 'No data found'})


class SalesReportApiView(APIView):
    """get sales reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get sales files"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file_df = pd.read_excel(serializer.validated_data['file'], engine='openpyxl')
            sales = file_df[
                ['Order Id', 'Creation Date', 'Customer Detail', 'Mobile', 'Email', 'Item Status', 'Total Amount']].copy()
            data = json.loads(sales.to_json(orient='records'))
            if data:
                return Response({'status': 'success', 'data': data})
        return Response({'status': 'failed', 'data': 'No data found'})


class ExceptionReportApiView(APIView):
    """get payment mode reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get mode of payment files"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file_df = pd.read_excel(serializer.validated_data['file'], engine='openpyxl')
            exceptions_data = file_df[
                ['transaction_entity', 'entity_id', 'amount', 'fee (exclusive tax)', 'tax', 'debit', 'payment_method', 'entity_created_at', 'order_id']].copy()
            exception_file = exceptions_data.groupby('transaction_entity')
            data = {}
            for exception_group_name, exception_group in exception_file:
                exception_group = exception_group.drop(columns=['transaction_entity'])
                if exception_group_name == 'refund':
                    data['exception'] = json.loads(exception_group.to_json(orient='records'))
                    data['exception'].append({'total_order_amount': round(exception_group['amount'].sum(), 2)})
                    data['exception'].append({'total_gateway_fee': round(exception_group['fee (exclusive tax)'].sum(), 2)})
                    data['exception'].append({'total_tax_amount': round(exception_group['tax'].sum(), 2)})
                    data['exception'].append({'total_debit_amount': round(exception_group['debit'].sum(), 2)})
            if data:
                return Response({'status': 'success', 'data': data})
        return Response({'status': 'failed', 'data': 'No data found'})


class SettlementReportApiView(APIView):
    """get payment mode reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get mode of payment files"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file_df = pd.read_excel(serializer.validated_data['file'], engine='openpyxl')
            settlement_data = file_df[
                ['transaction_entity', 'entity_id', 'amount', 'fee (exclusive tax)', 'tax', 'debit', 'credit', 'payment_method', 'entity_created_at', 'order_id', 'settlement_id', 'settlement_utr']].copy()
            settlement_file = settlement_data.groupby('settlement_utr')
            data = {}
            for settlement_group_name, settlement_group in settlement_file:
                settlement_group = settlement_group.drop(columns=['settlement_utr'])
                data[settlement_group_name] = json.loads(settlement_group.to_json(orient='records'))
                data[settlement_group_name].append({'total_order_amount': round(settlement_group['amount'].sum(), 2)})
                data[settlement_group_name].append({'total_gateway_fee': round(settlement_group['fee (exclusive tax)'].sum(), 2)})
                data[settlement_group_name].append({'total_tax_amount': round(settlement_group['tax'].sum(), 2)})
                data[settlement_group_name].append({'total_debit_amount': round(settlement_group['debit'].sum(), 2)})
                data[settlement_group_name].append({'total_credit_amount': round(settlement_group['credit'].sum(),2)})
            if data:
                return Response({'status': 'success', 'data': data})
        return Response({'status': 'failed', 'data': 'No data found'})


class TimeSettlementReport(APIView):
    """get payment mode reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get mode of payment files"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file_df = pd.read_excel(serializer.validated_data['file'], engine='openpyxl')
            settlement_data = file_df[
                ['transaction_entity', 'amount', 'fee (exclusive tax)', 'tax', 'debit', 'credit',
                'entity_created_at', 'settled_at', 'settlement_utr']].copy()

            d1 = settlement_data['entity_created_at'][64]
            d2 = settlement_data['settled_at'][64]
        return Response({'status': 'success', 'data': {'year': 2020, 'month': 'August', 'total_amount': 120015, 'T': 100, 'T+1': 200, 'T+2': 850, 'T+3': 50}})
