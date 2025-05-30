from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.utils.dateparse import parse_date
from .templates import *
from django.contrib.auth import authenticate, login as auth_login
# Create your views here.

def loginpage(request):
    return render(request, 'loginpage.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(username, password)

        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful!")
            return redirect(home)  
        else:
            messages.error(request, "Invalid username or password!")
            return redirect(loginpage)

def register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('registerpage')

        user = CustomUser.objects.create_user(first_name = fullname, username=email, password=password, email=email)
        user.save()
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('loginpage')

    return redirect(loginpage)

def home(request):
    user = request.user
    if not user.is_authenticated:
        return redirect(loginpage)
    notif=Notification.objects.filter(user=request.user).order_by('-created_at')
    ack=Acknowledgement.objects.filter(models.Q(to_user=request.user, status = 'pending')).order_by('-acknowledged_at')
    recent_transactions = Transaction.objects.filter(sender=request.user).order_by('-created_at')[:3]
    return render(request, 'dashboard.html', {'user': user, 'notif': notif, 'ack': ack, 'recent_transactions': recent_transactions})

def transac(request):
    return render(request, 'create-transaction.html')

def transac_create(request):
    if not request.user.is_authenticated:
        return redirect(loginpage)

    if request.method == 'POST':
        sender = request.user
        receiver_username = request.POST.get('reciever')
        transac_info = request.POST.get('data')
        proof = request.FILES.get('image1')

        print("Got'em", receiver_username)

        try:
            receiver = CustomUser.objects.get(first_name=receiver_username)
            print("Receiver found:", receiver)
            if receiver == sender:
                messages.error(request, "You cannot send money to yourself.")
                print("Error")
                return redirect(home)

            transaction = Acknowledgement(from_user=sender, to_user=receiver, image=proof, data=transac_info)
            print("Stored")
            transaction.save()
            messages.success(request, "Transaction created successfully!")
            return redirect(home)
        except CustomUser.DoesNotExist:
            messages.error(request, "Receiver does not exist.")
            return redirect(transac)

    return redirect(home)

def ack_action(request, ack_id, action):
    ack = get_object_or_404(Acknowledgement, id=ack_id, to_user=request.user)

    if ack.status != 'pending':
        return redirect(home)

    if action == 'accept':
        ack.status = 'accepted'
        ack.accepted_at = timezone.now()
        ack.save()

        Transaction.objects.create(sender=ack.from_user,receiver=ack.to_user,data=ack.data,image=ack.image,acknowledged_at=ack.acknowledged_at)

    elif action == 'reject':
        print("Rejected")
        ack.status = 'rejected'
        ack.save()

        Notification.objects.create(user=ack.from_user,message=f"Acknowledgement from {ack.from_user.first_name} was rejected.")
        print("Notification created")

    return redirect(home)

def transac_history(request):
    if not request.user.is_authenticated:
        return redirect(loginpage)
    transactions = Transaction.objects.filter(models.Q(sender=request.user) | models.Q(receiver=request.user)).order_by('-acknowledged_at')

    return render(request, 'transaction-history.html', {'transactions': transactions})

def transac_filter(request):
    if not request.user.is_authenticated:
        return redirect(loginpage)
    
    transactions = Transaction.objects.filter(sender=request.user).order_by('-acknowledged_at')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    name = request.GET.get('name')

    if start:
        transactions = transactions.filter(acknowledged_at__gte=parse_date(start))
    if end:
        transactions = transactions.filter(acknowledged_at__lte=parse_date(end))
    if name:
        transactions = transactions.filter(sender__first_name__icontains=name) | transactions.filter(receiver__first_name__icontains=name)

    return render(request, 'transaction-history.html', {'transactions': transactions})

def my_logout(request):
    return redirect(loginpage)
