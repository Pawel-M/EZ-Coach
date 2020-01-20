using TMPro;
using UnityEngine;

namespace EZCoach.Pong {
    public class HUD : MonoBehaviour {

        [SerializeField] private TextMeshProUGUI leftPlayerPointsText;
        [SerializeField] private TextMeshProUGUI rightPlayerPointsText;
        [SerializeField] private GameObject startButton;

        void Start() {
            Game.Round.pointsChangedEvent.AddListener(PointsChangedHandler);
            Game.Round.runningChangedEvent.AddListener(RunningChangedHandler);
        }

        private void RunningChangedHandler() {
            startButton.SetActive(!Game.Round.Running);
        }

        private void PointsChangedHandler() {
            leftPlayerPointsText.text = $"{Game.Round.LeftPlayerPoints}";
            rightPlayerPointsText.text = $"{Game.Round.RightPlayerPoints}";
        }
    }
}
