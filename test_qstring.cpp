#include <test_qstring.h>

namespace bindtest {
	QString hello_message_from_qt() {
		return QString("Hello from qt");
	}
	std::string hello_message_from_std() {
		return std:string("Hello from std");
	}
	void say_hello_with_qt(QString greetings) {
		qDebug() << greetings;
	}
	void say_hello_with_std(std::string greetings) {
		std::cerr << greetings;
	}
}
