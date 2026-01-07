# Phase 2 Features Guide

This document outlines the new features added in Phase 2 of the Alsakr V2 Platform.

## 1. Voice Search & Command
**Location**: Command Center (`/command-center`)

### Feature Description
Users can search for products and issue commands using their voice. The system records audio, transcribes it on the backend using `faster-whisper`, and executes the command via the Agent Orchestrator.

### Usage
1.  Locate the **Microphone Icon** in the sidebar.
2.  **Click to Start**: The icon pulses red.
3.  **Speak**: "Find me inductive sensors with stock."
4.  **Click to Stop**: The system processes the audio.
5.  **Result**: The transcribed text appears in the search bar and results are fetched.

### Technical Implementation
- **Frontend**: `MediaRecorder` API captures `audio/webm`.
- **Backend**: `app.core.voice_service.VoiceService` handles transcription.
- **Model**: Uses `faster-whisper` (default: small/tiny model on CPU).

## 2. Buyer Inquiry System
**Location**: Product Details Modal -> Request Quote

### Feature Description
Logged-in buyers (or guest buyers with ID) can request official quotes for specific products directly from the interface.

### Usage
1.  Click on a product to view details.
2.  Click **"Request Official Quote"**.
3.  The request is sent to the backend and stored in PocketBase.

## 3. Vendor Dashboard
**Location**: `/vendor/dashboard`

### Feature Description
A dedicated portal for vendors/admins to view incoming quotes and inquiries.

### Usage
- Navigate to `/vendor/dashboard`.
- View table of inquiries with Buyer ID, Product, and Status.
