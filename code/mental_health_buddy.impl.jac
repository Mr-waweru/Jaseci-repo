"""Implementation on mental_health_buddy.jac"""

impl MentalHealthBuddy.start {
    let mood = input("How are you feeling today? ");

    if mood in ["sad", "tired", "angry", "stressed", "anxious", "lonely"] {
        print("I’m sorry you’re feeling that way. Let me cheer you up...");
        let response = cheer_up(mood);
        print("Here's something for you:\n");
        print(response);
    } else {
        print(f"That’s wonderful! Keep enjoying your {mood} mood!");
    }
}
