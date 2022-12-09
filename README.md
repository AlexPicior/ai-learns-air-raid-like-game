# Summary of the project
 
 I used Python and different libraries to create an artificial intelligence that learns how to play an Air Raid like game.


 Firstly, with the library Pygame, I developed a game that has the following rules:
 - get a point for every alien ship destroyed 
 - lose if you let 15 alien ships pass by or the ship touches an alien ship


 Afterwards, I used NeuroEvolution of Augmenting Topologies (NEAT), a genetic algorithm, to build the artificial intelligence that learns how to play the game. The algorithm takes some input and gives output values between 0 and 1(it depends on the activation function), that represents the input and output nodes of the neural network. I used the absolute value of the difference in x and y between the ship and the closest alien ship and the x position of the ship as an input. The output, I selected to be a decision to perform one or more of the following actions: move left, move right, shoot.


 The performance of the AI:

 Generation 0-1: unable to understand how to move and shoot properly
 
![ai_learns_to_play_st_gen](https://user-images.githubusercontent.com/75032781/200827147-af6f494c-70b1-4f06-bd9f-9d1fba8a8d3e.gif)


Generation 7: starting to learn where and when to shoot and almost destroys every alien ship

![ai_learns_to_play_best_gen](https://user-images.githubusercontent.com/75032781/200835477-b24249ff-2460-4b7c-a13c-f413e0f29171.gif)


Generation 8: becomes unbeatable

![ai_learns_to_play_3](https://user-images.githubusercontent.com/75032781/206681085-ac2c5e7c-8e96-4dbf-82db-c77744860b3c.gif)
