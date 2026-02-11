
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class SimpleWebServer {

    public static void main(String[] args) throws IOException {
        // Create an HTTP server on port 8000
        HttpServer server = HttpServer.create(new InetSocketAddress(8000), 0);

        // Define a context that listens for requests at the root path "/"
        server.createContext("/", new RootHandler());

        // Start the server
        server.setExecutor(null); // Creates a default executor
        server.start();
        System.out.println("Server is running on http://localhost:8000/");
    }

    // Handler to process incoming HTTP requests
    static class RootHandler implements HttpHandler {

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            // Set the path to the HTML file
            Path filePath = Paths.get("index.html");

            // Send the HTTP response header with the correct content type and length
            byte[] fileBytes = Files.readAllBytes(filePath);
            exchange.getResponseHeaders().set("Content-Type", "text/html; charset=UTF-8");
            exchange.sendResponseHeaders(200, fileBytes.length);

            // Write the HTML file to the output stream
            OutputStream outputStream = exchange.getResponseBody();
            outputStream.write(fileBytes);
            outputStream.flush();
            outputStream.close();
        }
    }
}
