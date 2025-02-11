import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.io.ByteArrayOutputStream;

public class ChunkLink {

    // Custom exception for integrity validation
    static class IntegrityException extends Exception {
        IntegrityException(String message) {
            super(message);
        }
    }

    // Node class to represent each chunk in the linked list
    static class Node {
        byte[] data;          // File chunk data
        String nextChecksum;  // SHA-256 checksum of the next node's data
        Node nextNode;        // Pointer to the next node

        Node(byte[] data, String nextChecksum, Node nextNode) {
            this.data = data;
            this.nextChecksum = nextChecksum;
            this.nextNode = nextNode;
        }
    }

    // Function to split a file into fixed-size chunks
    public static List<byte[]> splitFile(byte[] fileData, int chunkSize) {
        if (chunkSize <= 0) {
            throw new IllegalArgumentException("Chunk size must be greater than zero");
        }

        List<byte[]> chunks = new LinkedList<>();
        for (int i = 0; i < fileData.length; i += chunkSize) {
            int end = Math.min(fileData.length, i + chunkSize);
            chunks.add(Arrays.copyOfRange(fileData, i, end));
        }
        return chunks;
    }

    // Custom method to convert byte array to hexadecimal string
    public static String toHexString(byte[] bytes) {
        StringBuilder hexString = new StringBuilder();
        for (byte b : bytes) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        return hexString.toString().toUpperCase(); // Return uppercase hexadecimal
    }

    // Function to compute SHA-256 checksum of a byte array
    public static String computeChecksum(byte[] data) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(data);
            return toHexString(hash);  // Use custom method to convert byte array to hex
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }

    // Function to create a linked list from chunks
    public static Node createLinkedList(List<byte[]> chunks) {
        if (chunks.isEmpty()) return null;

        List<String> checksums = new ArrayList<>();
        for (int i = 1; i < chunks.size(); i++) {
            checksums.add(computeChecksum(chunks.get(i)));
        }
        checksums.add(null); // Last node has no next checksum

        Node head = null, prevNode = null;
        for (int i = 0; i < chunks.size(); i++) {
            Node currentNode = new Node(chunks.get(i), checksums.get(i), null);
            if (prevNode != null) {
                prevNode.nextNode = currentNode;
            } else {
                head = currentNode;
            }
            prevNode = currentNode;
        }
        return head;
    }

    // Function to reconstruct the file from the linked list
    public static byte[] reconstructFile(Node head) {
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        Node current = head;
        while (current != null) {
            outputStream.write(current.data, 0, current.data.length);
            current = current.nextNode;
        }
        return outputStream.toByteArray();
    }

    // Function to validate the linked list using checksums
    public static void validateLinkedList(Node head) throws IntegrityException {
        Node current = head;
        while (current != null && current.nextNode != null) {
            String computedChecksum = computeChecksum(current.nextNode.data);
            if (!computedChecksum.equals(current.nextChecksum)) {
                throw new IntegrityException("Data corruption detected at node!");
            }
            current = current.nextNode;
        }
    }

    // Function to simulate corruption
    public static void simulateCorruption(Node head) {
        Random rand = new Random();
        List<Node> nodeList = new ArrayList<>();
        Node current = head;

        // Collect all nodes
        while (current != null) {
            nodeList.add(current);
            current = current.nextNode;
        }

        // If there are fewer than two nodes, we cannot corrupt the data meaningfully
        if (nodeList.size() < 2) {
            System.out.println("Not enough nodes to simulate corruption.");
            return;
        }

        // Select a random node to corrupt (excluding the last one to prevent issues)
        int corruptIndex = rand.nextInt(nodeList.size() - 1);
        Node corruptNode = nodeList.get(corruptIndex + 1);

        System.out.println("\nSimulating corruption at Chunk " + (corruptIndex + 1));

        // Corrupt the selected chunk
        byte[] corruptedData = Arrays.copyOf(corruptNode.data, corruptNode.data.length);
        corruptedData[0] ^= 0xFF; // Invert the first byte (corrupting the chunk)

        Node corruptedNode = new Node(corruptedData, corruptNode.nextChecksum, corruptNode.nextNode);
        nodeList.set(corruptIndex + 1, corruptedNode);

        // Recompute the checksums
        for (int i = 0; i < nodeList.size() - 1; i++) {
            nodeList.set(i, new Node(nodeList.get(i).data, computeChecksum(nodeList.get(i + 1).data), nodeList.get(i + 1)));
        }

        // Revalidate the linked list after corruption
        try {
            validateLinkedList(nodeList.get(0));
            System.out.println("Validation successful (unexpected)!");
        } catch (IntegrityException e) {
            System.out.println("Validation failed: " + e.getMessage());
        }

        // Reconstruct and print the file data after corruption
        byte[] reconstructedCorruptData = reconstructFile(nodeList.get(0));
        System.out.println("\nReconstructed (Corrupt) File Data: " + new String(reconstructedCorruptData, StandardCharsets.UTF_8));
    }

    // Main function to demonstrate the workflow
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        try {
            System.out.println("Enter the text data:");
            String inputData = scanner.nextLine();
            byte[] fileData = inputData.getBytes(StandardCharsets.UTF_8);

            int chunkSize = -1;
            while (chunkSize <= 0) {
                try {
                    System.out.println("Enter chunk size:");
                    chunkSize = Integer.parseInt(scanner.nextLine().trim());
                    if (chunkSize <= 0) {
                        throw new NumberFormatException();
                    }
                } catch (NumberFormatException e) {
                    System.out.println("Invalid input. Please enter a positive integer.");
                }
            }

            // Split the file into chunks
            List<byte[]> chunks = splitFile(fileData, chunkSize);

            // Create a linked list from the chunks
            Node head = createLinkedList(chunks);

            // Show the classified chunks with data and checksum
            System.out.println("\nClassified Chunks:");
            Node current = head;
            int index = 0;
            while (current != null) {
                System.out.print("Chunk " + index++ + ": ");
                System.out.println(new String(current.data, StandardCharsets.UTF_8) + " (Checksum: " + current.nextChecksum + ")");
                current = current.nextNode;
            }

            // Validate the linked list
            try {
                validateLinkedList(head);
                System.out.println("\nValidation successful: No data corruption detected.");
            } catch (IntegrityException e) {
                System.out.println("\nValidation failed: " + e.getMessage());
            }

            // Reconstruct and print the file data
            byte[] reconstructedData = reconstructFile(head);
            System.out.println("\nReconstructed File Data: " + new String(reconstructedData, StandardCharsets.UTF_8));

            // Simulate corruption
            System.out.println("\nDo you want to simulate corruption? (yes/no)");
            String response = scanner.nextLine();
            if (response.equalsIgnoreCase("yes")) {
                simulateCorruption(head);
            }

        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
}
