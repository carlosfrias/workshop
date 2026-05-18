#!/bin/bash
# Gist-based Communication Protocol
# Usage: 
#   Send to cloud:  ./gist-comm.sh send <message_type> <file>
#   Check from cloud: ./gist-comm.sh recv <message_type>
#   Post file to gist (requires gh auth): ./gist-comm.sh post <filename> <content_file>

GIST_ID="0c517214489cb78c0484ca661f3d8463"
GIST_BASE="https://gist.githubusercontent.com/carlosfrias/$GIST_ID/raw"

case "$1" in
    send)
        # Send message to cloud agent (displays for copy/paste OR posts if gh available)
        MSG_TYPE="$2"
        FILE="$3"
        
        echo "========================================"
        echo "SENDING TO CLOUD AGENT"
        echo "========================================"
        echo ""
        echo "Message type: $MSG_TYPE"
        echo "File: $FILE"
        echo ""
        
        if [ ! -f "$FILE" ]; then
            echo "✗ File not found: $FILE"
            exit 1
        fi
        
        # Try to post to Gist if gh is authenticated
        if command -v gh &> /dev/null && gh auth status &> /dev/null 2>&1; then
            echo "✓ GitHub CLI authenticated - posting to Gist..."
            gh gist edit "$GIST_ID" --add "$FILE" 2>/dev/null && echo "  ✓ Posted to Gist" || echo "  ⚠ Post failed"
            echo ""
            echo "Cloud agent will be notified."
        else
            echo "⚠ GitHub CLI not authenticated - displaying for manual copy:"
            echo ""
            echo "========================================"
            echo "COPY EVERYTHING BELOW THIS LINE"
            echo "========================================"
            echo ""
            echo "## Node 2 $MSG_TYPE"
            echo "**Time:** $(date -u)"
            echo "**Hostname:** $(hostname)"
            echo ""
            cat "$FILE"
            echo ""
            echo "========================================"
            echo "END OF MESSAGE"
            echo "========================================"
            echo ""
            echo "Paste the above to the cloud agent session on your Mac."
            echo ""
            echo "OR authenticate GitHub CLI for automatic posting:"
            echo "  gh auth login"
            echo "  Then re-run this command"
        fi
        echo ""
        ;;
    
    recv)
        # Receive message from cloud agent
        MSG_TYPE="$2"
        
        echo "========================================"
        echo "CHECKING FOR MESSAGES FROM CLOUD"
        echo "========================================"
        echo ""
        echo "Message type: $MSG_TYPE"
        echo ""
        
        case "$MSG_TYPE" in
            fix-commands)
                FILE="node2-fix-commands.sh"
                ;;
            complete)
                FILE="node2-COMPLETE.md"
                ;;
            status)
                FILE="node2-STATUS.md"
                ;;
            *)
                echo "Unknown message type: $MSG_TYPE"
                exit 1
                ;;
        esac
        
        echo "Checking Gist for: $FILE"
        echo ""
        
        if curl -sL "$GIST_BASE/$FILE" | grep -q "^#"; then
            echo "✓ Message found!"
            echo ""
            echo "Downloading..."
            curl -sL "$GIST_BASE/$FILE" -o "/tmp/$FILE"
            echo "  ✓ Saved to: /tmp/$FILE"
            echo ""
            echo "Contents:"
            echo "----------------------------------------"
            cat "/tmp/$FILE"
            echo "----------------------------------------"
            echo ""
            read -p "Execute this file? (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                echo "Executing..."
                bash "/tmp/$FILE"
            fi
        else
            echo "⚠ No message found yet"
            echo ""
            echo "Cloud agent hasn't posted $FILE yet."
            echo "Check again in a few moments."
            echo ""
            echo "Manual check:"
            echo "  curl -L $GIST_BASE/$FILE"
        fi
        echo ""
        ;;
    
    post)
        # Post file to Gist (requires gh auth)
        FILENAME="$2"
        CONTENT="$3"
        
        if [ ! -f "$CONTENT" ]; then
            echo "✗ File not found: $CONTENT"
            exit 1
        fi
        
        if ! command -v gh &> /dev/null; then
            echo "✗ GitHub CLI (gh) not installed"
            echo "Install: https://cli.github.com/"
            exit 1
        fi
        
        if ! gh auth status &> /dev/null 2>&1; then
            echo "✗ GitHub CLI not authenticated"
            echo "Run: gh auth login"
            exit 1
        fi
        
        echo "Posting $FILENAME to Gist..."
        gh gist edit "$GIST_ID" --add "$CONTENT"
        echo "✓ Posted"
        ;;
    
    status)
        echo "========================================"
        echo "GIST COMMUNICATION STATUS"
        echo "========================================"
        echo ""
        echo "Gist ID: $GIST_ID"
        echo "URL: https://gist.github.com/carlosfrias/$GIST_ID"
        echo ""
        echo "Checking authentication..."
        if command -v gh &> /dev/null && gh auth status &> /dev/null 2>&1; then
            echo "  ✓ GitHub CLI authenticated"
            echo "  ✓ Can send/receive automatically"
        else
            echo "  ⚠ GitHub CLI not authenticated"
            echo "  ✓ Can receive from Gist"
            echo "  ✗ Must copy/paste to send"
            echo ""
            echo "To enable automatic sending:"
            echo "  1. Install: https://cli.github.com/"
            echo "  2. Run: gh auth login"
        fi
        echo ""
        echo "Recent messages from cloud:"
        for f in node2-fix-commands.sh node2-COMPLETE.md node2-STATUS.md; do
            if curl -sL "$GIST_BASE/$f" | grep -q "^#"; then
                echo "  ✓ $f (available)"
            else
                echo "  - $f (not found)"
            fi
        done
        echo ""
        ;;
    
    *)
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  send <type> <file>     - Send message to cloud (auto if gh auth, else copy/paste)"
        echo "  recv <type>            - Receive message from cloud (fix-commands, complete, status)"
        echo "  post <name> <file>     - Post file to Gist (requires gh auth)"
        echo "  status                 - Show communication status"
        echo ""
        echo "Message types:"
        echo "  diagnostic             - Diagnostic output"
        echo "  results                - Fix execution results"
        echo "  fix-commands           - Commands from cloud (recv only)"
        echo "  complete               - Completion notice (recv only)"
        echo "  status                 - Status update"
        echo ""
        exit 1
        ;;
esac
