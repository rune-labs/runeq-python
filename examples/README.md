# Jupyter Notebook Templates

The Rune Labs application programming interface (API) provides access to deidentified data from our database. (This data cannot be used to identify an individual "patient.")

This data is acquired from a growing number of sources, including:
* The StrivePD app for the iPhone and Apple Watch
* Apple's movement disorder kit (MM4PD, tremor and dyskinesia metrics)
* Apple's Health ecosystem
* Deep brain stimulation devices
* etc.

The Rune Labs software development kit (SDK), called `runeq`, is a set of tools intended to simplify usage of our API. These tools are currently available in the Python programming language.

For detailed information:
* [Rune Labs API documentation](https://docs.runelabs.io/stream/v2/)
* [Rune Labs SDK documentation](https://runeq.readthedocs.io/en/latest/)
* [Rune Labs open source code respository](https://github.com/rune-labs/runeq-python/tree/main/examples)

---

## Tutorials

These tutorials will guide you through the process of setting up a Python environment, installing the Rune Labs SDK (`runeq`), setting up access credentials, and beginning to use the API/SDK to explore data.

0. [Python Installation Instructions](00_python_installation_instructions.md) <br>
details how to set up a Python analysis environment on an Apple computer (MacOS). These instructions can be skipped if you already have Anaconda installed

1. [Getting Started with the Rune Labs API/SDK](01_getting_started_with_Rune_SDK.ipynb) <br>
walks through installation of the Rune Labs SDK (`runeq`) and initializing it with your account credentials

2. [Exploring Organizations and Patients](02_exploring_organizations_and_patients.ipynb) <br>
demonstrates the basic steps of exploring the organizations and patients to which you have access

3. [Exploring Patient Devices](03_exploring_patient_devices.ipynb) <br>
demonstrates the basic steps of exploring the devices associated with each patient

4. [Querying Stream Metadata](04_querying_stream_metadata.ipynb) <br>
demonstrates the basic steps of querying and exploring stream metadata, which describes and parameterized each stream of data, and is used in later steps to retrieve the desired data

5. [Pulling Stream Data](05_pulling_stream_data.ipynb) <br>
demonstrates the basic steps of pulling streams of data using queried stream metadata

6. [Understanding Types of Data Streams](06_stream_types.ipynb) <br>
explains the structure of data "stream types" that are returned by the Rune Labs API

7. [Checking Data Availability](07_checking_data_availability.ipynb) <br>
demonstrates how to check data availability using "availability" representations, including how to find overlapping data streams

---

## Examples

These examples demonstrate common workflows performed using the Rune Labs API/SDK, and can be used a templates to customize for your own applications.

* [Coming soon...]() <br>
More workflow examples will be available soon

* [Coming soon...]() <br>
More workflow examples will be available soon

---

## Appendix of Functions

Handy utility functions found in the above tutorials and examples:

**Function** | **Notebook**
--- | --- 
`plot_availability` | [Checking Data Availability](07_checking_data_availability.ipynb)