/******************************************************************************

                              Online C++ Compiler.
               Code, Compile, Run and Debug C++ program online.
Write your code in this editor and press "Run" button to compile and execute it.

*******************************************************************************/

#include <iostream>
#include<conio.h>
using namespace std;

class Rectangle
{      //data members
    private:
	int l,b,Area,Peri;
	//member functions
    public:
	void accept_Data()
	{
	       cout<<"\nEnter the values for length and breadth";
	       cin>>l>>b;
	       cal_Area(l,b);
	       cal_Peri(l,b);
	}

    private:
	void cal_Area(int l,int b)
	{
		Area = l*b;
		print_Output(Area);
	}
	void cal_Peri(int l,int b)
	{
		Peri = 2*(l+b);
		print_Output(Peri);
	}
	void print_Output(int out)
	{
		cout<<"\nOutput="<<out;
	}
 };

int main()
{
    //clrscr();
    Rectangle obj;//object of type Test - class
    obj.accept_Data(); //private
   // o1.data2=20; //public
   // o1.func_A();      //public
   // o1.func_B();      //private
    //getch();
    return 0;
}

