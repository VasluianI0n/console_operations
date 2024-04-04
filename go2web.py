import socket
import argparse
import re
import requests
from bs4 import BeautifulSoup

def fetch_url(url):
    try:
        # Make an HTTP GET request to the specified URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the response
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text from HTML, excluding tags
            text = soup.get_text()

            # Print the human-readable response
            print(text)
        elif response.status_code == 301 or response.status_code == 302:
            # If the status code indicates a redirect, print the redirect location
            print(f"Redirected to: {response.headers['Location']}")
        else:
            print(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching URL: {url}. Exception: {e}")

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
