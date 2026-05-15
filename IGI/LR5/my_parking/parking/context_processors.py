from .models import CompanyInfo

def company_data(request):
    # Берем самую первую запись о компании
    info = CompanyInfo.objects.first()
    return {'company_global': info}
