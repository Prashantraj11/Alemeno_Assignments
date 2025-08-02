from django.core.management.base import BaseCommand
from loans.tasks import ingest_all_data
from loans.models import Customer, Loan


class Command(BaseCommand):
    help = 'Load customer and loan data from Excel files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run data ingestion as async Celery task',
        )

    def handle(self, *args, **options):
        customer_count = Customer.objects.count()
        loan_count = Loan.objects.count()
        
        if customer_count > 0 or loan_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'Data already exists: {customer_count} customers, {loan_count} loans. Skipping ingestion.'
                )
            )
            return

        if options['async']:
            # Run as Celery task
            self.stdout.write('Starting async data ingestion...')
            task = ingest_all_data.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Task started with ID: {task.id}')
            )
        else:
            # Run synchronously
            self.stdout.write('Starting synchronous data ingestion...')
            result = ingest_all_data()
            
            customer_result = result.get('customer_ingestion', {})
            loan_result = result.get('loan_ingestion', {})
            
            if customer_result.get('status') == 'success':
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Customers: {customer_result.get('customers_created', 0)} created, "
                        f"{customer_result.get('customers_updated', 0)} updated"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Customer ingestion failed: {customer_result.get('message', 'Unknown error')}"
                    )
                )
            
            if loan_result.get('status') == 'success':
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Loans: {loan_result.get('loans_created', 0)} created, "
                        f"{loan_result.get('loans_updated', 0)} updated"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Loan ingestion failed: {loan_result.get('message', 'Unknown error')}"
                    )
                )
