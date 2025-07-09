<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
<div align="center">

  <a href="https://github.com/Terry-BrooksJr/nhhc_workplace_management_system/issues">
    <img src="https://img.shields.io/github/issues/Terry-BrooksJr/nhhc_workplace_management_system.svg?style=for-the-badge" alt="GitHub Issues">
  </a>
  <a href="https://github.com/Terry-BrooksJr/nhhc_workplace_management_system/blob/master/LICENSE.txt">
    <img src="https://img.shields.io/github/license/Terry-BrooksJr/nhhc_workplace_management_system.svg?style=for-the-badge" alt="License">
  </a>
  <a href="https://linkedin.com/in/terryabrooks">
    <img src="https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555" alt="LinkedIn">
  </a>

</div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Terry-BrooksJr/nhhc_workplace_management_system">
    <img src="https://nhhc-chicago.nyc3.digitaloceanspaces.com/static/img/CareNettLogo.png" alt="Logo" width="580" height="380">
  </a>
  <h3 align="center">NHHC Workplace Management System</h3>
  <p align="center">
    The NHHC Workplace Management System is a custom comprehensive tool for user management.    <br />
    <a href="https://github.com/Terry-BrooksJr/nhhc_workplace_management_system/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/Terry-BrooksJr/nhhc_workplace_management_system/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

<img src="https://nhhc-chicago.nyc3.digitaloceanspaces.com/static/img/readme.png"/>

[Product Name Screen Shot][product-screenshot]](http://netthandshome.care)

The NHHC Workplace Management System is a custom comprehensive tool designed to streamline workplace operations by managing resources, employees, and daily tasks in a centralized system. Built with Python, Django, and PostgreSQL, it facilitates efficient operations, performance tracking, and resource allocation.

It is a bespoke HRIS system that is customized around contractual requirements set forth by Partner of the Illinois Department of Aging. At the time of this writing, any client or patient information has been excluded.

This application makes no claims to be HIPPA compliant. While it's design does follow the core precepts of data privacy and security in the United States, it does require individualized production harding.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## CareNett Django Application Architecture

```mermaid
graph TD
    A[Django Application] --> B[Security Middleware]
    A --> C[Caching Layer]
    A --> D[Authentication]
    A --> E[Logging]
    A --> F[Background Workers]

    B --> B1[CSRF Protection]
    B --> B2[SSL Redirect]
    B --> B3[XSS Filter]

    C --> C1[Redis Cache]
    C --> C2[Session Cache]
    C --> C3[Celery Cache]

    D --> D1[AllAuth]
    D --> D2[Custom Employee Model]
    D --> D3[Defender Login Protection]

    E --> E1[Loguru Logger]
    E --> E2[Logtail Handler]

    F --> F1[Celery]
    F --> F2[Background Task Queue]

    G[Database] --> A
    G --> H[PostgreSQL]
    G --> I[SSL Encrypted Connection]

    J[Storage] --> A
    J --> K[AWS S3]
    J --> L[Private/Public Media Storage]

    M[Monitoring] --> N[Prometheus]
    M --> O[Health Checks]
```
## Built With

* Primary Coding Language: Python (V3.12.5)
* Frameworks: [![Static Badge](https://img.shields.io/badge/Django-DBMS?style=for-the-badge&logo=django&logoColor=white&logoSize=auto&label=V.5.1.1&labelColor=%23092E20&color=%23092E20&cacheSeconds=3600)](https://www.djangoproject.com/https://www.django.org)
* Database/DBMS: Relational - [![Static Badge](https://img.shields.io/badge/Postgres-DBMS?style=for-the-badge&logo=postgresql&logoColor=white&logoSize=auto&label=V.16&labelColor=%230064a5&color=%23d24b03&cacheSeconds=3600)](https://www.postgresql.org/)
* Cache Data Store: DragonFly DB [![PostgreSQL][PostgreSQL.com]][PostgreSQL-url]
* Secrets Management: Doppler

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

* Python 3.11+

```sh
sudo apt-get install python3
```

### Installation

1. Clone the repo

```sh
git clone https://github.com/Terry-BrooksJr/nhhc_workplace_management_system.git
```

2. Install Python packages

```sh
pip install -r requirements.txt
```

3. Set up the database

```sh
python manage.py migrate
```

4. Run the development server

```sh
python manage.py runserver
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

This system can be used for managing daily operations, tracking employee performance, and handling resource allocation within the workplace.

_For more examples, please refer to the [User Manual](http://docs.netthandshome.care)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [ ] Printing Employee Profiles For Auditing
- [ ] Enhancing Announcements to also send SMS announcements campaigns
- [ ] Develop Resource Management Module
- [ ] Add Employee Performance Tracking
- [ ] Integrate with third-party tools

See the [open issues](https://github.com/Terry-BrooksJr/nhhc_workplace_management_system/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/Terry-BrooksJr/nhhc_workplace_management_system/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Terry-BrooksJr/nhhc_workplace_management_system" alt="contrib.rocks image" />
</a>

<!-- LICENSE -->

## License

Distributed under the GNU General Public License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Terry Brooks Jr - [@twitter_handle](https://twitter.com/NomadicSaaS_PM) - terry.brooks@brooksjr.com

Project Link: [https://github.com/Terry-BrooksJr/nhhc_workplace_management_system](https://github.com/Terry-BrooksJr/nhhc_workplace_management_system)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<div align="center">

  <a href="https://github.com/Terry-BrooksJr/nhhc_workplace_management_system/issues">
    <img src="https://img.shields.io/github/issues/Terry-BrooksJr/nhhc_workplace_management_system.svg?style=for-the-badge" alt="GitHub Issues">
  </a>
  <a href="https://github.com/Terry-BrooksJr/nhhc_workplace_management_system/blob/master/LICENSE.txt">
    <img src="https://img.shields.io/github/license/Terry-BrooksJr/nhhc_workplace_management_system.svg?style=for-the-badge" alt="License">
  </a>
  <a href="https://linkedin.com/in/terryabrooks">
    <img src="https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555" alt="LinkedIn">
  </a>

</div>




