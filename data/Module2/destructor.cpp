// C++ program to demonstrate the number of times
// constructor and destructors are called

#include <iostream>
using namespace std;
int cCount = 0;
int dCount = 0;
class Test {
public:
	// User-Defined Constructor
	Test()
	{

		// Number of times constructor is called
		cCount++;
		cout << "No. of Object created: " << cCount
			<< endl;
	}

	// User-Defined Destructor
	~Test()
	{
		dCount++;
		cout << "No. of Object destroyed: " << dCount
			<< endl;
		// Number of times destructor is called
	}
};

// driver code
int main()
{
	Test t, t1, t2, t3;

	return 0;
}

