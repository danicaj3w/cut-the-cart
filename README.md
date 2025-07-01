# Cut the Cart
If you're lazy like me, you probably don't want to spend your time shopping through different stores looking for different deals. This app was made to help people quickly search up products and compare prices between stores nearby.

## What does it currently do?
Currently, the user is able to input a search query for some products and see a list of all the different brands that Kroger has in its databse. The user can input multiple items, for ex: "milk,cereal".

## Tech Stack
### Backend
- AWS Lambda
- Trigger: API Gateway
- API: [Kroger Products and Locations](https://developer.kroger.com/api-products)
- Database: DynamoDB

### Frontend
- Typescript
- Tailwind CSS

## Future implementation
The app should have an input for the user's zip code, which would allow them to select the nearest Kroger store to buy their items from. Ideally, the app would also be able to access inventory of other grocery stores, either through some database created from scraping sitemaps or APIs provided by the grocery store.

## What did I learn?
I worked on this application from 6/20 - 6/30. This application consisted of three main parts: Getting grocery store data, configuring Lambda properly and testing responses, and displaying the data on my website. 

#### <u>Getting Data</u>
My initial approach was to scrape websites such as Target using Selenium, however this goes against their Terms of Service (ToS). The other approach was to go through Target's sitemaps and store all the data collected in a database, however this posed problems because it would take a considerable amount of space to comb through all the links for every product Target has ever sold. I opted to go for the Kroger API, which freely provides its developers an API for its products and locations of nearby stores. However, this limited the original implementation I had planned for my app because I couldn't access other grocery stores. Regardless, I wanted to get experience with using AWS Lambda, so this was the best option at the moment. 

#### <u>Configuring Lambda</u>
First of all, it's important to read the documentation before starting. Going into the hackathon, I had no idea what AWS Lambda was or how to configure it properly. I spent a substantial amount of time trying to diagnose errors that resulted because of AWS Lambda not being configured properly. I had to deal with setting environment variables correctly, making sure my handlers were running in Python, and setting API Gateway permissions correctly. I also needed to figure out how to correctly link my DynamoDB to the Lambda function properly.

#### <u>Connecting the frontend</u>
I learned how to use Typescript and Tailwind CSS for a simple project. I was rather unfamiliar with the changes, but using my knowledge of React and CSS, I was able to figure out how the different languages translated. I also made a quick Figma prototype, but found myself making several iterations as I explored the ideas of integrating more features.

## What I would do better next time
Based on the problems I mentioned above, I would plan my idea out better and start off smaller. Given the limitations of the data I could collect, there wasn't much room to fully implement what I intended and I couldn't implement all the features I wanted to within the deadline. I would also break down what I needed to learn for each section better and dedicate a bit more time in the beginning to getting a better understanding of features and capabilities. For example, the Kroger API itself needed two parts to achieve the end goal, which was getting the prices of each item to rank them. However, I realized later on during development that I needed the Locations API, so this wasn't set up in time.