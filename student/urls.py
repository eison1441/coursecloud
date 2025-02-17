
from django.urls import path
from student import views

urlpatterns = [

    path('register/',views.StudentAddView.as_view(),name="student-create"),
    path("signin/",views.SigninView.as_view(),name="signin"),
    path("index/",views.IndexView.as_view(),name="index"),
    path("signout/",views.SignOutView.as_view(),name="signout"),
    path("courses/<int:pk>/",views.CourseDetailView.as_view(),name="course-detail"),
    path("courses/<int:pk>/add-to-cart",views.AddToCartView.as_view(),name="add-to-cart"),
    path("cart/summery",views.CartSummeryView.as_view(),name="cart-summery"),
    path("cart/<int:pk>/remove",views.CartItemDeleteView.as_view(),name="cart-item-delete"),
    path("checkout/",views.CheckOutView.as_view(),name="checkout"),
    path("mycourse/",views.MyCoursesView.as_view(),name="My-Courses"),
    path("courses/<int:pk>/watch/",views.LessonDetailView.as_view(),name="lesson-detail"),
    path("payment/verify",views.PaymentVerificationView.as_view(),name="payment-verify"),

   
]