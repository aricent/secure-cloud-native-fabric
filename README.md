# SCF - Secure Cloud Native Fabric
SCF enables goal-based visibility into changes in security control configurations that implement regulatory compliance requirements as well as organizational security policies so that appropriate action can be taken in real-time. Capabilities enabled by SCF include:   
* Security configuration posture tracking of Kubernetes container orchestrator and multi-cloud infrastructure    
* Tracking real-time compliance—such as CIS, GDPR—posture impacted by security control configuration    
* Application workload behavior posture tracking  

## Functional Architecture
![Functional Architecture](./documentation/images/scf_component.jpg)

## Compliance Real-time Impact on Securit Posture (CRISP) 
* Define security goals and their relationship with security control configurations in different asset    
* Associate different auditors to monitor security control configurations    
* Real-time impact security analysis on compliance and best practices due to changes in security configurations in different security controls in different assets    
* Determine risk score based on asset importance and criticality of changes    

## Secure Container Runtime Management (SCRM) 
* Management of security group policies, perimeter security policies, container runtime and networking security policies of a container cluster        
* Holistic small-unit visibility and workload identity based zero-trust communication model    

## Installation    

**Prerequisite** Application setup should be run on Linux.

1) Clone the repository   
2) Run the shell script from SCF folder to download all the dependencies required to make this application run 
    ./installer.sh 

## Use cases   

**1) SD-WAN for Telco**   
* SCF can be used to secure SDN applications forming a SD-WAN network   
* SCF Security Postures can be exported from CI/DI environments to a Production Environment   
* SCF can monitor security-alarms and auto-act on them   
* It can audit Security-Configurations and scan vulnerabilities in Registry Images   

**2) Apply and Monitor Security Posture**   
* SCF can be used to secure a Content Delivery Network (CDN) service hosted by a Telco   
* The Telco can provide CDN as a Service, for popular content.   
* Video and data from the Origin-Server are pulled into the CDN Point-of-Presence servers distributed across the Geographies   
* SCF can secure the end-point security policies and also audit the S3-Storage in a Hybrid Cloud environment   

**3) Mobile Edge Computing (MEC)**   
* SCF would require the Kubernetes API server access-account and credentials as a manifest file from the Cloud Orchestrator   
* SCF would require credentials of the private Docker Repository for setting up Image-Scanning   
* An SCF Agent Application, will be installed on the Kubernetes-Master Host, for setting up secure-communications on a distributed high-performance message-bus with the SCF Server-Application.   
* SCF Agent will use CIS Benchmark rules (configurable) Security Audits. It will enforce Network-Policies using the CNI through the Kube-API Gateway.   

## Tour of SCF   
**1) Goal Driven Security and Compliance with SCF-CRISP**   
    1.1) [Create Security Goals as a Posture in SCF](./documentation/making_postures.md)   
    1.2) [Create Audit Rules for Compliance monitoring](./documentation/create_auditRules.md)   
    1.3) [Monitor with Alarms](./documentation/alarms_monitoring.md)   

**2) Continuous Security with SCF-SCRM**   
    2.1) [View the Cloud Topology as a Social Graph](./documentation/view_topology.md)   
    2.2) [Security across Hybrid Cloud Deployments](./documentation/hybrid_cloud.md)   


## Third party plugins   
Following are client and server side dependencies on which our application run:

* **Bootstrap 3**    
    * It is a free and open-source CSS framework directed at responsive, mobile-first front-end web development. It contains CSS- and (optionally) JavaScript-based design templates for typography, forms, buttons, navigation and other interface components.
    * **License -** MIT
* **JQuery**  
    * jQuery is a JavaScript library designed to simplify HTML DOM tree traversal and manipulation, as well as event handling, CSS animation, and Ajax.
    * **License -** MIT
* **Font Awesome**    
    * Font Awesome is a font and icon toolkit based on CSS and LESS.
    * **License -** MIT
* **AngularJS**       
    * It is a JavaScript-based open-source front-end web framework mainly maintained by Google and by a community of individuals and corporations to address many of the challenges encountered in developing single-page applications.   
    * **License -** MIT
* **D3 JS**    
    * It is a JavaScript library for producing dynamic, interactive data visualizations in web browsers. It makes use of the widely implemented Scalable Vector Graphics, HTML5, and Cascading Style Sheets standards.    
    * **License -** BSD
* **Yaml Editor**    
    * This is an implementation of YAML, a human-friendly data serialization language.    
    * **License -** MIT
* **Contextual Menu**    
    * A context menu is a menu in a graphical user interface that appears upon user interaction, such as a right-click mouse operation.
    * **License -** MIT
* **Footable JS**   
    * A responsive table plugin built on jQuery.
    * **License -** MIT
* **Gauge JS**    
    * It is a handy JavaScript plugin for generating and animating nice & clean dashboard gauges.
    * **License -** MIT
* **Charts JS**    
    * Simple, clean and engaging HTML5 based JavaScript charts. Chart.js is an easy way to include animated, interactive graphs.
    * **License -** MIT
* **FastClick JS**      
    * It is a simple, easy-to-use library for eliminating the 300ms delay between a physical tap and the firing of a click event on mobile browsers. The aim is to make your application feel less laggy.
    * **License -** MIT
* **Bootbox**   
    * It is a tiny jQuery plugin for creating alert, confirm and flexible dialog boxes using Twitter's Bootstrap framework.
    * **License -** MIT
* **JQV Maps**   
    * It is a jQuery plugin that renders Interactive, Clickable Vector Maps. It uses resizable Scalable Vector Graphics (SVG) for modern browsers.
    * **License -** MIT OR GPL-3.0
* **JS Tree**       
    * It is jquery plugin, that provides interactive trees. It is easily extendable, themable and configurable, it supports HTML & JSON data sources and AJAX loading.
    * **License -** MIT
* **Flowchart JS**       
    * It is a jQuery & jQuery UI based flowchart plugin which enables you to create drag'n'drop flowchart boxes and connect between them with a custom line.
    * **License -** MIT
* **Neo4j Graphs**       
    * It is a graph visualization and analysis platform. It connects directly to Neo4j's graph database technology.
    * **License -** MIT
* **Elastic search**    
    * Elasticsearch is a highly-scalable document storage engine that specializes in search. The JSON-based nature of Elasticsearch, along with its simple REST API, make it easy to learn.
    * **License -** Apache 2.0
* **Python 3**    
    * It is an interpreted, high-level, general-purpose programming language used on a server to create web applications.
    * **License -** Python Software Foundation License (PSFL) is a BSD-style, permissive free software license which is compatible with the GNU General Public License (GPL)
* **Pip 3**    
    * PIP is a package manager for Python packages, or modules.
* **Nginx**    
    * Nginx is a web server which can also be used as a reverse proxy, load balancer, mail proxy and HTTP cache.
    * **License -** 2-clause BSD
* **Nats messaging system**       
    * NATS Server is a simple, high performance open source messaging system for cloud native applications, IoT messaging, and microservices architectures.
    * **License -** Apache 2.0
* **Nameko Microservices**   
    * Nameko is a framework for building microservices in Python.
    * **License -** Apache 2.0
