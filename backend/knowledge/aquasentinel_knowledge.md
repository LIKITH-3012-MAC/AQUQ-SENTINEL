# AquaSentinel AI Project Knowledge Base

## Overview
AquaSentinel AI is an advanced marine intelligence platform designed to monitor, detect, and mitigate marine pollution and environmental risks. It leverages satellite imagery, AI-powered debris detection, and regional environmental data to provide actionable intelligence for citizens, researchers, and maritime authorities.

## Core Features
1. **Marine Intelligence Dashboard**: Real-time visualization of ocean health scores, active alerts, and recent reports.
2. **Global Intelligence Map**: Interactive Leaflet-based map with layers for Chlorophyll-a, Sea Surface Temperature (SST), and marine risk heatmaps.
3. **AI Debris Detection**: Automated analysis of satellite and ground imagery to identify plastics, nets, and other pollutants.
4. **Marine Reporting System**: 6-step tactical protocol for reporting environmental anomalies with GPS and image support.
5. **Dynamic Risk Engine**: Advanced formula-based scoring considering debris density, thermal stress (SST), and biological stress (Chl).
6. **AI Copilot**: Groq-powered intelligent assistant for user guidance and project technical support.

## User Journey
1. **Discovery**: Users land on a futuristic landing page explaining ocean protection.
2. **Onboarding**: Users register or login to the Command Base.
3. **Operational Command**: Access the dashboard to see regional metrics.
4. **Tactical Action**: View the map for anomalies or report an issue via the Tactical Protocol.
5. **AI Analysis**: Check automated debris detection results and risk assessments.

## Technical Architecture
- **Frontend**: Vanilla HTML/CSS/JS (Cyber-Premium design) hosted on Vercel.
- **Backend**: Python FastAPI hosted on Render.
- **Database**: PostgreSQL (Aiven) with UUID primary keys for secure identification.
- **AI Engine**: Groq (Llama 3.3/3.1) for LLM capabilities.
- **Data Sources**: NASA GIBS (Satellite layers), OpenWeather (Marine weather), Copernicus (Ocean currents).

## Role-Based Access (RBAC)
- **User (Citizen)**: Simple reporting and basic dashboard access.
- **Researcher**: Technical metrics, technical map layers, and detailed data points.
- **NGO**: Action-focused insights and community impact analysis.
- **Authority**: High-level operational command and alert management.
- **Admin**: Full system control and user management.

## Risk Engine Formula
Risk Score (0-100) = (Debris Density * 0.3) + (Thermal Stress * 0.2) + (Biological Stress * 0.2) + (Dynamic Weather Stress * 0.2) + (Community Reports * 0.1).

## Regional Language Support
AquaSentinel detects user location and provides responses in regional languages:
- **Andhra Pradesh/Telangana**: Telugu
- **Tamil Nadu**: Tamil
- **Karnataka**: Kannada
- **Kerala**: Malayalam
- **North India**: Hindi
Responses always include a primary English summary for official records.

## Troubleshooting
- **Login Issues**: Ensure cookies are enabled and JWT token is stored in localStorage.
- **Map Not Loading**: Check internet connection for Leaflet tiles; verify API base URL in config.js.
- **Report Failure**: Ensure image upload completes before submitting the final tactical report.

## FAQ
- **Is the data real-time?**: Satellite layers are refreshed every 24-48 hours via NASA GIBS. Weather is real-time.
- **Who manages the reports?**: Reports are verified by regional authorities and AI verification pipelines.
- **Can I use it offline?**: No, AquaSentinel requires an active link to the Intelligence OS (Backend).
