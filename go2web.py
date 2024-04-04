import socket
import argparse
import re
import requests
from bs4 import BeautifulSoup

def fetch_url(url):
    # Extract host and path to use in the HTTP GET request
    host = url.split("//")[-1].split("/")[0]
    path = url.split(host)[-1]
    if path == "":
        path = "/"

    try:
        while True:
            # Create a socket and connect to the server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, 80))
                s.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())

                # Receive the response and decode it
                response = s.recv(4096).decode()

                # Check for redirection (status codes 301 or 302)
                if 'HTTP/1.1 301' in response or 'HTTP/1.1 302' in response:
                    # Extract the new location from the response headers
                    new_location = re.search(r'Location: (.+?)\r\n', response).group(1)
                    # Update the host and path for the new location
                    host = new_location.split("//")[-1].split("/")[0]
                    path = new_location.split(host)[-1]
                    if path == "":
                        path = "/"
                else:
                    # No redirection, return the response
                    # Simple HTML tag stripping for readability
                    clean_response = re.sub('<[^<]+?>', '', response)
                    print(clean_response)
                    return clean_response
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

def google_search(query):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect the socket to the Google server
    server_address = ('www.google.com', 80)
    sock.connect(server_address)

    # Set a timeout for the socket
    sock.settimeout(5)  # Timeout set to 5 seconds

    # Construct the HTTP request
    request = f"GET /search?q={query.replace(' ', '+')} HTTP/1.1\r\nHost: www.google.com\r\n\r\n"

    # Send the request
    sock.sendall(request.encode())

    # Receive the response
    response = ''
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data.decode('latin-1')  # Decode using 'latin-1' encoding
    except socket.timeout:
        pass  # Timeout occurred, stop receiving data

    # Close the socket
    sock.close()

    # Use regular expressions to extract search results
    links = re.findall(r'<a href="/url\?q=(.*?)&amp;', response)
    titles = re.findall(r'class="BNeawe vvjwJb AP7Wnd">(.*?)</div>', response)

    # Display top 10 results
    for i in range(10):
        if i < len(titles) and i < len(links):
            print("Title:", titles[i])
            print("Link:", links[i])
            print()
    
    user_input = int(input("Please enter the number of the site you want to be redirected to: "))
    fetch_url(links[user_input])

def main():
    parser = argparse.ArgumentParser(description='Simple CLI for HTTP Requests and Search')
    parser.add_argument('-u', '--url', help='Fetch content from URL')
    parser.add_argument('-s', '--search', help='Search term')

    args = parser.parse_args()

    if args.search:
        google_search("cats")
    elif args.url:
        fetch_url(args.url)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
