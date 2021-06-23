#include <test_qstring.h>

namespace bindtest {
	QString TestQString::hello_message_from_qt() {
		return QString("Hello from qt");
	}
	std::string TestQString::hello_message_from_std() {
		return std:string("Hello from std");
	}
	void TestQString::say_hello_with_qt(QString greetings) {
		qDebug() << greetings;
	}
	void TestQString::say_hello_with_std(std::string greetings) {
		std::cerr << greetings;
	}
}
