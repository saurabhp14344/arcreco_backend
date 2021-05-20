from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserUploadFileSerializer, TotalReconcileSerializer, ReportSerializer
from .models import UploadFiles, TotalReconcile
from core.models import UserCompanyLogo
import pandas as pd
from django.db.models import Sum
import numpy as np
from core.permissions import UpdateOwnProfile
import timestring
import json
from arcreco import settings


class UserUploadFileApiView(generics.CreateAPIView, generics.ListAPIView):
    """Upload files"""
    permission_classes = (IsAuthenticated, UpdateOwnProfile)
    queryset = UploadFiles.objects.all()
    serializer_class = UserUploadFileSerializer

    def get_queryset(self):
        return self.queryset.filter(user_profile=self.request.user)

    def post(self, request, *args, **kwargs):
        """Upload files by user post endpoint"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            files = dict(request.data.lists())['file']
            types = dict(request.data.lists())['type']
            flag = 1
            arr = []
            for key, value in zip(types, files):
                file_name = value.name.split('.')[0]
                file_serializer = self.serializer_class(data={'name': file_name, 'type': key, 'file': value})
                if file_serializer.is_valid():
                    file_serializer.save(user_profile=self.request.user)
                    arr.append(file_serializer.data)
                else:
                    flag = 0
                    arr.append(file_serializer.data)

            if flag == 1:
                return Response({'status': 'success', 'data': arr}, status=status.HTTP_201_CREATED)
            else:
                return Response(arr, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # This is for single file upload
        # if serializer.is_valid():
        #     filename = serializer.validated_data['file']
        #     data_name = request.data.get('file').name
        #     uploaded = data_name.split('.')
        #     serializer.validated_data['name'] = uploaded[0]
        #     df = pd.read_excel(filename, engine='openpyxl')
        # if df.empty is False:
        #     if UploadFiles.objects.filter(user_profile_id=request.user.id).filter(
        #             name=serializer.validated_data['name']).first() is None:
        #         serializer.save(user_profile=self.request.user)
        #         return Response({'status': 'success',
        #                          'message': "File upload successfully."
        #                          }, status=status.HTTP_201_CREATED)
        #     else:
        #         return Response({
        #             'status': 'failed',
        #             'message': "File exist.Please choose different file."
        #         })
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MatchFilesApiView(generics.ListAPIView):
    """get report matched data"""
    permission_classes = (IsAuthenticated,)
    queryset = UploadFiles.objects.all()
    serializer_class = TotalReconcileSerializer

    def post(self, request):
        """get the user file matched data"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            order_file = UploadFiles.objects.get(id=serializer.validated_data['file1_id'])
            gateway_file = UploadFiles.objects.get(id=serializer.validated_data['file2_id'])
            file_1_df = pd.read_excel(order_file.file, engine='openpyxl')
            col_range = list(np.arange(0, 19, 1))
            col_range = col_range[:2] + col_range[3:]
            file_2_df = pd.read_excel(gateway_file.file, usecols=col_range, engine='openpyxl')
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
                columns={'_merge': 'Status', 'Order Id': 'order_id', 'Creation Date': 'creation_date',
                         'Customer Detail': 'customer_detail', 'Total Amount': 'total_amount'})
            csv2["Status"].replace({"left_only": "unmatched", "both": "matched", "right_only": "unmatched"},
                                   inplace=True)
            csv2 = csv2.groupby('Status', as_index=False)

            emp_d = {}

            # df11 = pd.DataFrame({'name': ['User 4', 'User 5']})
            # print(connection)
            # df11.to_sql('users_dummy', con=connection, if_exists='append')

            for df_group_name, df_group in csv2:
                df_group = df_group.drop(columns=['Status'])
                emp_d[df_group_name] = json.loads(df_group.to_json(orient='records'))
                # df_group.to_sql(name="table1", con=connection, if_exists="append")
            # append partial unmatched
            emp_d['partial_unmatched'] = []

            serializer.create(profile=self.request.user,
                              name=order_file.name,
                              sales_count=len(file_1_df.index),
                              reconcile_count=csv2.size()['matched'],
                              ageing_count=ageing['COD'],
                              start_date=timestring.Date(start_date),
                              end_date=timestring.Date(end_date)
                              )
            return Response({'status': 'success', 'data': emp_d, 'rows_reconciled': len(file_1_df.index),
                             'matched_entries': csv2.size()['matched'], 'unmatched_entries': csv2.size()['unmatched']})
            # csv2.to_csv('filename_here.csv', index=False)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TotalFilesApiView(APIView):
    """count uploaded documents"""
    permission_classes = (IsAuthenticated,)
    total_ageing = 0
    total_reconcile = 0
    total_sales = 0

    def get(self, request, format=None):
        logo = UserCompanyLogo.objects.filter(users=self.request.user)
        user_count = UploadFiles.objects.filter(user_profile=self.request.user).count()
        sales = TotalReconcile.objects.filter(user_profile=self.request.user)
        reconcile = TotalReconcile.objects.filter(user_profile=self.request.user)
        ageing = TotalReconcile.objects.filter(user_profile=self.request.user)
        all_data = {}
        sale_lst = []
        reconcile_lst = []
        ageing_lst = []

        if sales:
            for sale in sales:
                data = {
                    'date': sale.start_date.strftime("%B %Y"),
                    'sales_count': sale.sales_count
                }
                if not any(sale_d['date'] == sale.start_date.strftime("%B %Y") for sale_d in sale_lst):
                    sale_lst.append(data)
            self.total_sales = sales.aggregate(Sum('sales_count'))['sales_count__sum']

        if reconcile:
            for recon in reconcile:
                data = {
                    'date': recon.start_date.strftime("%B %Y"),
                    'reconcile_count': recon.reconcile_count
                }
                if not any(reconcile_d['date'] == recon.start_date.strftime("%B %Y") for reconcile_d in reconcile_lst):
                    reconcile_lst.append(data)
            self.total_reconcile = reconcile.aggregate(Sum('reconcile_count'))['reconcile_count__sum']

        if ageing:
            for age in ageing:
                data = {
                    'date': age.start_date.strftime("%B %Y"),
                    'ageing_count': age.ageing_count
                }
                if not any(ageing_d['date'] == age.start_date.strftime("%B %Y") for ageing_d in ageing_lst):
                    ageing_lst.append(data)
            self.total_ageing = ageing.aggregate(Sum('ageing_count'))['ageing_count__sum']

        content = {
            'total_uploaded_files': user_count,
            'sales': sale_lst,
            'total_sales': self.total_sales,
            'reconcile': reconcile_lst,
            'total_reconcile': self.total_reconcile,
            'ageing': ageing_lst,
            'total_ageing': self.total_ageing,
            'rows_reconciled': 0,
            'matched_entries': 0,
            'unmatched_entries': 0,
        }
        all_data['dashboard_data'] = content
        all_data['time_reconcile'] = [{
            'date': 'August 2020',
            'total': 2850250.00,
            't': 0.00,
            't1': 560962.00,
            't2': 1256083.00,
            't3': 1033205.00
        },
            {
                'date': 'September 2020',
                'total': 2650250.00,
                't': 0.00,
                't1': 460962.00,
                't2': 1156083.00,
                't3': 1033205.00
            },
            {
                'date': 'October 2020',
                'total': 2750250.00,
                't': 0.00,
                't1': 460962.00,
                't2': 1156083.00,
                't3': 1133205.00
            },
            {
                'date': 'November 2020',
                'total': 2350250.00,
                't': 0.00,
                't1': 260962.00,
                't2': 1056083.00,
                't3': 1033205.00
            },
            {
                'date': 'December 2020',
                'total': 2950250.00,
                't': 0.00,
                't1': 560962.00,
                't2': 1356083.00,
                't3': 1033205.55
            }]

        all_data['day_reconcile'] = [{
            'date': 'July 2020',
            'settlement_amount': 2450250.00,
            'bank_amount': 2450250.00,
            'open_amount': 260962.00,
            'outstanding': 0.00,
        },
            {
                'date': 'August 2020',
                'settlement_amount': 2730154.00,
                'bank_amount': 2730154.00,
                'open_amount': 120096.00,
                'outstanding': 0.00,
            },
            {
                'date': 'September 2020',
                'settlement_amount': 2548155.00,
                'bank_amount': 2650250.00,
                'open_amount': 102095.00,
                'outstanding': 0.00,
            },
            {
                'date': 'October 2020',
                'settlement_amount': 2459143.00,
                'bank_amount': 2459143.00,
                'open_amount': 291107.00,
                'outstanding': 0.00,
            },
            {
                'date': 'November 2020',
                'settlement_amount': 2180897.00,
                'bank_amount': 2180897.00,
                'open_amount': 169353.00,
                'outstanding': 0.00,
            }]

        if logo:
            all_data['company_logo'] = f"http://{request.get_host()}{settings.MEDIA_URL}{str(logo.last().logo)}"
        else:
            all_data['company_logo'] = None
        return Response({
            'status': 'success',
            'data': all_data
        })


class AgeingReportApiView(APIView):
    """get ageing reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get COD report files pass order file id in query params"""
        serializer = self.serializer_class(data=request.query_params)
        if serializer.is_valid():
            get_file = UploadFiles.objects.get(id=serializer.data['file_id'])
            file_df = pd.read_excel(get_file.file, engine='openpyxl')
            ageing_csv = file_df[
                ['Order Id', 'Creation Date', 'Customer Detail', 'Mobile', 'Item Status', 'Total Amount']].copy()
            ageing = ageing_csv.rename(
                columns={'Order Id': 'order_id', 'Creation Date': 'creation_date', 'Customer Detail': 'customer_detail',
                         'Mobile': 'mobile', 'Item Status': 'item_status', 'Total Amount': 'total_amount'})
            file_ageing = ageing.groupby('item_status')
            data = {}
            for ageing_group_name, ageing_group in file_ageing:
                ageing_group = ageing_group.drop(columns=['item_status'])
                if ageing_group_name == 'COD':
                    data['ageing'] = json.loads(ageing_group.to_json(orient='records'))
                    data['total_order_amount'] = round(ageing_group['total_amount'].sum(), 2)
            if data:
                return Response({'status': 'success', 'data': data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModePaymentReportApiView(APIView):
    """get payment mode reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get mode of payment files pass payment gateway file id in query params"""
        serializer = self.serializer_class(data=request.query_params)
        if serializer.is_valid():
            get_file = UploadFiles.objects.get(id=serializer.data['file_id'])
            file_df = pd.read_excel(get_file.file, engine='openpyxl')
            payment_mode = file_df[
                ['entity_id', 'payment_method', 'amount', 'fee (exclusive tax)', 'tax', 'debit', 'credit',
                 'entity_created_at', 'order_id']].copy()
            payment = payment_mode.rename(
                columns={'fee (exclusive tax)': 'fee_tax'})
            payment_mode_file = payment.groupby('payment_method')
            data = {}
            for payment_group_name, payment_group in payment_mode_file:
                payment_group = payment_group.drop(columns=['payment_method'])
                data[payment_group_name] = json.loads(payment_group.to_json(orient='records'))
                data[payment_group_name + "_total_amount"] = {
                    'total_order_amount': round(payment_group['amount'].sum(), 2),
                    'total_gateway_fee': round(payment_group['fee_tax'].sum(), 2),
                    'total_tax_amount': round(payment_group['tax'].sum(), 2),
                    'total_debit_amount': round(payment_group['debit'].sum(), 2),
                    'total_credit_amount': round(payment_group['credit'].sum(), 2)
                }
                # data[payment_group_name].append(
                #     {'total_gateway_fee': round(payment_group['fee_tax'].sum(), 2)})
                # data[payment_group_name].append({'total_tax_amount': round(payment_group['tax'].sum(), 2)})
                # data[payment_group_name].append({'total_debit_amount': round(payment_group['debit'].sum(), 2)})
                # data[payment_group_name].append({'total_credit_amount': round(payment_group['credit'].sum(), 2)})
            if data:
                return Response({'status': 'success', 'data': data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalesReportApiView(APIView):
    """get sales reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get sales files pass order file id in query params"""
        serializer = self.serializer_class(data=request.query_params)
        if serializer.is_valid():
            get_file = UploadFiles.objects.get(id=serializer.data['file_id'])
            file_df = pd.read_excel(get_file.file, engine='openpyxl')
            sales = file_df[
                ['Order Id', 'Creation Date', 'Customer Detail', 'Mobile', 'Email', 'Item Status',
                 'Total Amount']].copy()
            sale = sales.rename(
                columns={'Order Id': 'order_id', 'Creation Date': 'creation_date', 'Customer Detail': 'customer_detail',
                         'Mobile': 'mobile', 'Item Status': 'item_status', 'Total Amount': 'total_amount',
                         'Email': 'email'})
            data = json.loads(sale.to_json(orient='records'))
            if data:
                return Response({'status': 'success', 'data': data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExceptionReportApiView(APIView):
    """get payment mode reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get mode of payment files pass payment gateway file id in query params"""
        serializer = self.serializer_class(data=request.query_params)
        if serializer.is_valid():
            get_file = UploadFiles.objects.get(id=serializer.data['file_id'])
            file_df = pd.read_excel(get_file.file, engine='openpyxl')
            exceptions_d = file_df[
                ['transaction_entity', 'entity_id', 'amount', 'fee (exclusive tax)', 'tax', 'debit', 'payment_method',
                 'entity_created_at', 'order_id']].copy()
            exceptions_data = exceptions_d.rename(
                columns={'fee (exclusive tax)': 'fee_tax'})
            exception_file = exceptions_data.groupby('transaction_entity')
            data = {}
            for exception_group_name, exception_group in exception_file:
                exception_group = exception_group.drop(columns=['transaction_entity'])
                if exception_group_name == 'refund':
                    data['exception'] = json.loads(exception_group.to_json(orient='records'))
                    data["exception_total_amount"] = {
                        'total_order_amount': round(exception_group['amount'].sum(), 2),
                        'total_gateway_fee': round(exception_group['fee_tax'].sum(), 2),
                        'total_tax_amount': round(exception_group['tax'].sum(), 2),
                        'total_debit_amount': round(exception_group['debit'].sum(), 2),
                    }
                    # data['total_order_amount'] = round(exception_group['amount'].sum(), 2)
                    # data['total_gateway_fee'] = round(exception_group['fee_tax'].sum(), 2)
                    # data['total_tax_amount'] = round(exception_group['tax'].sum(), 2)
                    # data['total_debit_amount'] = round(exception_group['debit'].sum(), 2)
            if data:
                return Response({'status': 'success', 'data': data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SettlementReportApiView(APIView):
    """get payment mode reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get mode of payment files pass payment gateway file id in query params"""
        serializer = self.serializer_class(data=request.query_params)
        if serializer.is_valid():
            get_file = UploadFiles.objects.get(id=serializer.data['file_id'])
            file_df = pd.read_excel(get_file.file, engine='openpyxl')
            settlement_d = file_df[
                ['transaction_entity', 'entity_id', 'amount', 'fee (exclusive tax)', 'tax', 'debit', 'credit',
                 'payment_method', 'entity_created_at', 'order_id', 'settlement_id', 'settlement_utr']].copy()
            settlement_data = settlement_d.rename(
                columns={'fee (exclusive tax)': 'fee_tax'})
            settlement_file = settlement_data.groupby('settlement_utr')
            data = {}
            for settlement_group_name, settlement_group in settlement_file:
                settlement_group = settlement_group.drop(columns=['settlement_utr'])
                data[settlement_group_name] = json.loads(settlement_group.to_json(orient='records'))
                data[settlement_group_name + "_total_amount"] = {
                    'total_order_amount': round(settlement_group['amount'].sum(), 2),
                    'total_gateway_fee': round(settlement_group['fee_tax'].sum(), 2),
                    'total_tax_amount': round(settlement_group['tax'].sum(), 2),
                    'total_debit_amount': round(settlement_group['debit'].sum(), 2),
                    'total_credit_amount': round(settlement_group['credit'].sum(), 2)
                }
                # data[settlement_group_name].append({'total_order_amount': round(settlement_group['amount'].sum(), 2)})
                # data[settlement_group_name].append(
                #     {'total_gateway_fee': round(settlement_group['fee_tax'].sum(), 2)})
                # data[settlement_group_name].append({'total_tax_amount': round(settlement_group['tax'].sum(), 2)})
                # data[settlement_group_name].append({'total_debit_amount': round(settlement_group['debit'].sum(), 2)})
                # data[settlement_group_name].append({'total_credit_amount': round(settlement_group['credit'].sum(), 2)})
            if data:
                return Response({'status': 'success', 'data': data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeSettlementReport(APIView):
    """get payment mode reports"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get(self, request):
        """get mode of payment files pass payment file id in query params"""
        serializer = self.serializer_class(data=request.query_params)
        if serializer.is_valid():
            get_file = UploadFiles.objects.get(id=serializer.data['file_id'])
            file_df = pd.read_excel(get_file.file, engine='openpyxl')
            settlement_data = file_df[
                ['transaction_entity', 'amount', 'fee (exclusive tax)', 'tax', 'debit', 'credit',
                 'entity_created_at', 'settled_at', 'settlement_utr']].copy()

            d1 = settlement_data['entity_created_at'][64]
            d2 = settlement_data['settled_at'][64]
        return Response({'status': 'success',
                         'data': {'year': 2020, 'month': 'August', 'total_amount': 120015, 'T': 100, 'T+1': 200,
                                  'T+2': 850, 'T+3': 50}})
