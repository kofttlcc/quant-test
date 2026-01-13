
import express from 'express';
import cors from 'cors';
import skillRoutes from './routes/skillRoutes';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.use('/api', skillRoutes);

app.get('/', (req, res) => {
    res.send('Skill Antigravity Server is running');
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
