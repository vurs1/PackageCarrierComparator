# Package Carrier Comparator

I built this web app to solve my own shipping headaches. Currently, it compares rates from 2 shipping carriers (UPS & USPS) in real-time. I utilized **Shippo's** API Key to fetch real shipping rates and built this full-stack app using **Flask** and **JavaScript/Bootstrap**.

![Image](https://github.com/user-attachments/assets/ecba4f02-39c4-4733-b0b8-ec2d6620a8cd)

## Features

- **Real-time rate comparison** from USPS and UPS
- **Smart recommendations** - automatically highlights cheapest and fastest options
- **Easy to use** - just enter your package dimensions and weight
- **Instant results** - get shipping options sorted by price

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Shipping API**: Shippo API
  
## Supported Carriers

Currently supports:

- **USPS**: Priority Mail, Ground Advantage, Priority Mail Express
- **UPS**: Ground, 2nd Day Air, Next Day Air, and more

## Quick Start

### Prerequisites

- Python 3.7+
- Shippo API token

### Setup

1. **Clone the repo**

   ```bash
   git clone <your-repo-url>
   cd PackageComparator
   ```

2. **Install dependencies**

   ```bash
   pip install flask requests python-dotenv
   ```

3. **Set up your API token**

   ```bash
   cd src
   # Add your Shippo API token to .env file
   echo "SHIPPO_API_TOKEN=your_token_here" > .env
   ```

4. **Run the app**

   ```bash
   python3 app.py
   ```

## How to Use

1. **Enter your package details**:

   - Weight (in pounds)
   - Length (in inches)
   - Width (in inches)
   - Height (in inches)

2. **Click "Compare Carriers"**

3. **View your options**:
   - Prices sorted from lowest to highest
   - Cheapest and fastest options highlighted
   - Delivery time estimates

## Project Structure

```
PackageCarrierComparator/
├── README.md              # This file
├── src/
│   ├── app.py            # Main Flask application
│   └── templates/
│       └── index.html    # Frontend interface
```

## API Endpoints

- `GET /`: Main page
- `POST /compare`: Get shipping rates
  - **Input**: JSON with weight, length, width, height
  - **Output**: JSON with shipping options and recommendations

## Note
I was only able to add USPS and UPS (2 carriers) to the current project since the test version of Shippo's API only allows 2 carriers. Their "live key" is required to see more carriers.

## Troubleshooting

If you run into issues:

1. Check that your Shippo API token is valid
2. Make sure all dependencies are installed
3. Verify package dimensions are within carrier limits
4. Check browser console for any JavaScript errors

## Links

- [Shippo API Docs](https://goshippo.com/docs/)
- [Bootstrap Docs](https://getbootstrap.com/docs/)
- [Flask Docs](https://flask.palletsprojects.com/)
