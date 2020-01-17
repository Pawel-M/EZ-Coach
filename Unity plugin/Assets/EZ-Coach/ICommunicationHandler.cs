using System.Collections.Generic;
using UnityEngine;

namespace EZCoach {
    /// <summary>
    /// An interface which is used to handle messages received from the Training Module.
    /// </summary>
    public interface ICommunicationHandler {
        /// <summary>
        /// Handles the connect message by sending the game's manifest to the Training Module.
        /// </summary>
        void HandleConnect();
        
        /// <summary>
        /// Handles the start message by starting a game's round.
        /// </summary>
        /// <param name="numPlayers">a number of players selected by the Training Module</param>
        /// <param name="options">a dictionary of options</param>
        void HandleStart(int numPlayers, Dictionary<string, object> options = null);
        
        /// <summary>
        /// Handles actions selected by the agent's.
        /// </summary>
        /// <param name="actions">a list of actions of each player</param>
        void HandleActions(object[] actions);
        
        /// <summary>
        /// Handles stop by stopping current round.
        /// </summary>
        void HandleStop();
    }
}