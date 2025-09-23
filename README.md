# Contract Analyzer

AI-powered contract analysis and negotiation assistance with enterprise security.

## Table of Contents

- [About The Project](#about-the-project)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## About The Project

This project is an AI-powered contract analysis and negotiation assistance tool. It provides enterprise-grade security features to ensure that your contracts are handled with the utmost care.

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

- Docker
- Python 3.11+
- Poetry

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/your_username_/contract-analyzer.git
   ```
2. Install dependencies
   ```sh
   poetry install
   ```
3. Set up the environment
   ```sh
   make setup
   ```

## Usage

You can run the application using Docker with the following commands:

- `make dev`: Run in development mode with hot-reloading.
- `make prod`: Run in production mode.
- `make stop`: Stop the application.
- `make logs`: View the application logs.

For a full list of commands, run `make help`.

## Project Structure

```
├── backend
│   ├── app
│   └── tests
├── config
├── data
├── frontend
├── logs
├── sample_contracts
├── scripts
└── venv
```

- **backend**: Contains the FastAPI backend application.
- **config**: Contains configuration files.
- **data**: Contains data used by the application, such as databases and vector stores.
- **frontend**: Contains the Streamlit frontend application.
- **logs**: Contains log files.
- **sample_contracts**: Contains sample contracts for testing.
- **scripts**: Contains utility scripts for deployment, monitoring, etc.
- **venv**: Contains the Python virtual environment.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter) - email@example.com

Project Link: [https://github.com/your_username_/contract-analyzer](https://github.com/your_username_/contract-analyzer)

