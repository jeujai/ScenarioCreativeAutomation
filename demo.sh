#!/bin/bash

echo "=================================================="
echo "Creative Automation Pipeline - Demo"
echo "=================================================="
echo ""
echo "This is a command-line tool for generating social ad campaign assets."
echo "It runs on-demand, generates the assets, and exits."
echo ""
echo "Usage examples:"
echo "  python main.py examples/campaign_brief.yaml"
echo "  python main.py examples/campaign_brief.json --verbose"
echo ""
echo "Running example campaign..."
echo ""

python main.py examples/campaign_brief.yaml

echo ""
echo "=================================================="
echo "Demo completed! Check outputs/ directory for results."
echo "=================================================="
