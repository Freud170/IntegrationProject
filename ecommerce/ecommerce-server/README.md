# Spring Boot Server

This project is a simple Spring Boot application that demonstrates how to handle GET requests using a RESTful approach. The application includes a single endpoint that returns a greeting message.

## Project Structure

```
spring-boot-server
├── src
│   ├── main
│   │   ├── java
│   │   │   └── com
│   │   │       └── example
│   │   │           └── server
│   │   │               ├── ServerApplication.java
│   │   │               └── controller
│   │   │                   └── HelloController.java
│   │   └── resources
│   │       ├── application.properties
│   │       └── static
│   └── test
│       └── java
│           └── com
│               └── example
│                   └── server
│                       └── ServerApplicationTests.java
├── build.gradle
├── settings.gradle
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd spring-boot-server
   ```

2. **Build the project:**
   ```
   ./gradlew build
   ```

3. **Run the application:**
   ```
   ./gradlew bootRun
   ```

4. **Access the endpoint:**
   Open your browser and navigate to `http://localhost:8080/hello` to see the greeting message.

## Usage

This application serves a simple greeting message at the `/hello` endpoint. You can modify the `HelloController` class to change the message or add more endpoints as needed.

## Dependencies

This project uses Spring Boot and other necessary dependencies defined in the `build.gradle` file. Make sure to check the file for any additional configurations or dependencies you may need.

## Testing

The project includes a basic test suite located in `src/test/java/com/example/server/ServerApplicationTests.java`. You can run the tests using the following command:

```
./gradlew test
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.