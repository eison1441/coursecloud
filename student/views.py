from django.shortcuts import render,redirect

from django.views.generic import View,TemplateView,FormView

from django.contrib.auth import authenticate,login,logout
# Create your views here.
from django.urls import reverse_lazy

from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator

from student.decorators import signin_required

from student.forms import StudentCreationForm,SigninForm

from instructor.models import Course,Cart,Order,Module,Lesson

from django.db.models import Sum

from decouple import config


import razorpay


RZP_KEY_ID=config('RZP_KEY_ID')

RZP_KEY_SECRET=config("RZP_KEY_SECRET")





class StudentAddView(View):

    def get(self,request,*args,**kwargs):

        form_instance=StudentCreationForm()

        return render(request,"student.html",{"form":form_instance})
    

    def post(self,request,*args,**kwargs):

        form_data=request.POST

        form_instance=StudentCreationForm(form_data)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("signin")
        
        else:
            return render(request,"signin",{"form":form_instance})
        

class SigninView(FormView):

    # def get(self,request,*args,**kwargs):

        # form_instance=SigninForm()

        # return render(request,"",{"form":form_instance})

    template_name="signin.html"
    form_class=SigninForm

    def post(self,request,*args,**kwargs):

        form_data=request.POST

        form_instance=SigninForm(form_data)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            uname=data.get("username")

            pwd=data.get("password")

            user_obj=authenticate(request,username=uname,password=pwd)

            if user_obj:

                login(request,user_obj)

                print("success")

                return redirect("index")
            else:

                print("invalid")
                return render(request,"student.html")

@method_decorator(signin_required,name="dispatch")
class SignOutView(View):   

    def get(self,request,*args,**kwargs):

        logout(request)        

        return redirect("signin")



       
            
@method_decorator(signin_required,name="dispatch")        
class IndexView(View):
    
    def get(self,request,*args,**kwargs):

        all_courses=Course.objects.all()

        purchased_courses=Order.objects.filter(student=request.user).values_list("course_objects",flat=True)

        return render(request,"index.html",{"courses":all_courses,"purchased_courses":purchased_courses})



@method_decorator(signin_required,name="dispatch")
class CourseDetailView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        course_instance=Course.objects.get(id=id)


        return render(request,"Course.html",{"course":course_instance})
     
        

@method_decorator(signin_required,name="dispatch")        
class AddToCartView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        course_instance=Course.objects.get(id=id)

        user_instance=request.user

        
        # Cart.objects.create(course_object=course_instance,user=user_instance)

        cart_instance,created=Cart.objects.get_or_create(course_object=course_instance,user=user_instance)

        print(created)
        return redirect("index")
    
@method_decorator(signin_required,name="dispatch")
class CartSummeryView(View):

    def get(self,request,*args,**kwargs):

        qs=request.user.basket.all()

        cart_summery=qs.values("course_object__price").aggregate(total=Sum("course_object__price")).get("total")

        print(cart_summery)

        return render(request,"cart-summery.html",{"carts":qs,"basket_total":cart_summery})
@method_decorator(signin_required,name="dispatch")    
class CartItemDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        cart_instance=Cart.objects.get(id=id)

        if cart_instance.user != request.user:

            return redirect("index")

        Cart.objects.get(id=id).delete()

        return redirect("cart-summery")
    
@method_decorator(signin_required,name="dispatch")
class CheckOutView(View):

    def get(self,request,*args,**kwargs):

        cart_items=request.user.basket.all()

        order_totlal=sum([ci.course_object.price for ci in cart_items])

        order_instance=Order.objects.create(student=request.user,total=order_totlal)

        for ci in cart_items:

            order_instance.course_objects.add(ci.course_object)

            ci.delete()

        order_instance.save()

        if order_totlal>0:
            client = razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))

            data = { "amount": int(order_totlal*100), "currency": "INR", "receipt": "order_rcptid_11" }

            payment = client.order.create(data=data)

            print(payment,"*************************************")

            rzp_id=payment.get("id")

            order_instance.rzp_order_id=rzp_id

            order_instance.save()

            context={
                "rzp_key_id":RZP_KEY_ID,
                "amount":int(order_totlal*100),
                "rzp_order_id":rzp_id,


            }

            return render(request,"payment.html",context)
        
        elif order_totlal==0:

        
            order_instance.is_paid=True

            order_instance.save()
    
        
        

        return redirect("index")
    
@method_decorator(signin_required,name="dispatch")
class MyCoursesView(View):

    def get(self,request,*args,**kwargs):

        Courses=request.user.purchase.filter(is_paid=True)
        print(Courses)

        return render(request,"Mycourese.html",{"orders":Courses})
@method_decorator(signin_required,name="dispatch")    
#Localhost:8000/student/Courses/1/watch?module-1&lesson-4
class LessonDetailView(View):

    def get(self,request,*args,**kwargs):

       course_id=kwargs.get("pk")

       course_instance=Course.objects.get(id=course_id) 

       purchased_course=request.user.purchase.filter(is_paid=True).values_list("course_objects",flat=True)

       if course_instance.id not in purchased_course:
           
           return redirect("index")

    #    request.GET={"module":1,"lesson":1}
       query_params=request.GET

       module_id=query_params.get("module") if "module" is query_params else course_instance.modules.all().first().id

       

       module_instance=Module.objects.get(id=module_id,course_object=course_instance)
       
       lesson_id=query_params.get("lesson") if "lesson" is query_params else module_instance.lessons.all().first().id
       lesson_instance=Lesson.objects.get(id=lesson_id,module_object=module_instance)


       return render(request,"lesson_details.html",{"course":course_instance,"lesson":lesson_instance})


@method_decorator(csrf_exempt,name="dispatch")

class PaymentVerificationView(View):

    def post(self,request,*args,**kwargs):

        print(request.POST,"******************~!!!!!!!!@@@@@@@@@")

        client = razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(request.POST)

            print("payment success")

            rzp_order_id=request.POST.get("razorpay_order_id")
            
            order_instance=Order.objects.get(rzp_order_id=rzp_order_id)

            order_instance.is_paid=True

            order_instance.save()

        except:

            print("faild!!!")        

        return redirect("index")