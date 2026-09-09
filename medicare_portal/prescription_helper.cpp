/*
    Optional C++ component.

    The Flask application itself is written in Python because Python is the
    web server/backend. This C++ file demonstrates how the same project could
    include a native C++ utility, for example a simple validation tool.

    Compile:
      g++ prescription_helper.cpp -o prescription_helper

    Run:
      ./prescription_helper
*/

#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>

bool hasRequiredFields(const std::string& medicine,
                       const std::string& dosage,
                       const std::string& frequency,
                       const std::string& duration) {
    // A real clinical application needs much more validation.
    return !medicine.empty() && !dosage.empty()
        && !frequency.empty() && !duration.empty();
}

int main() {
    std::string medicine, dosage, frequency, duration;

    std::cout << "Medicine: ";
    std::getline(std::cin, medicine);
    std::cout << "Dosage: ";
    std::getline(std::cin, dosage);
    std::cout << "Frequency: ";
    std::getline(std::cin, frequency);
    std::cout << "Duration: ";
    std::getline(std::cin, duration);

    if (hasRequiredFields(medicine, dosage, frequency, duration))
        std::cout << "Prescription fields look complete.\n";
    else
        std::cout << "One or more required fields are empty.\n";

    return 0;
}
