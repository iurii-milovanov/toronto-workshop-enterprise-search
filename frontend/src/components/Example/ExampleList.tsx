import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
};

const EXAMPLES: ExampleModel[] = [
    {
        text: "Case Studies for Agriculture",
        value: "Case Studies for Agriculture"
    },
    { text: "What we have for Automotive?", value: "What we have for Automotive?" },
    { text: "Blockchain expertise", value: "Blockchain expertise" },
    { text: "Who is the CTO of SoftServe?", value: "CTO of SoftServe?" },
    { text: "Prospecting email about our AI capabilities", value: "Write a prospecting email to a company interested in SoftServe's AI capabilities" },
    { text: "Data Scientist job description (Retail, AWS stack)", value: "Write a job description for a Data Scientist (Retail industry, AWS stack)" },
];

interface Props {
    onExampleClicked: (value: string) => void;
}

export const ExampleList = ({ onExampleClicked }: Props) => {
    return (
        <ul className={styles.examplesNavList}>
            {EXAMPLES.map((x, i) => (
                <li key={i}>
                    <Example text={x.text} value={x.value} onClick={onExampleClicked} />
                </li>
            ))}
        </ul>
    );
};
