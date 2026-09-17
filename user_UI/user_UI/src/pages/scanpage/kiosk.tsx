import ScanPage from './index';

export default function KioskScanPage() {
  return (
    <div className="kiosk-scan-page">
      <ScanPage kiosk />
      <style>{`
        .kiosk-scan-page {
          min-height: 100vh;
          background: #fff8f3;
          color: #263238;
          font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        .kiosk-scan-page > div {
          min-height: 100vh;
          box-sizing: border-box;
          padding: 16px 24px 32px;
          background: #fff8f3;
        }

        .kiosk-scan-page > div > div {
          max-width: 100%;
        }

        .kiosk-scan-page header {
          margin-bottom: 16px;
          border-radius: 18px;
          padding: 16px 24px;
          background: linear-gradient(115deg, #9b3d20, #d36a3e);
          box-shadow: 0 8px 22px rgba(117, 48, 27, .18);
        }

        .kiosk-scan-ai {
          min-height: 220px;
          margin: 0 0 18px;
          padding: 14px 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          border: 1px solid #e4b08e;
          border-radius: 18px;
          background: linear-gradient(135deg, #69351f, #a85b35);
          box-shadow: 0 8px 20px rgba(117, 48, 27, .14);
        }

        .kiosk-scan-ai img {
          display: block;
          width: min(100%, 760px);
          height: 190px;
          object-fit: contain;
          object-position: center;
        }

        .kiosk-scan-page main {
          border-radius: 20px;
          padding: 20px;
          background: #fff;
          box-shadow: 0 12px 32px rgba(117, 48, 27, .1);
          ring-color: #efc7b5;
        }

        .kiosk-scan-page .grid.xl\\:grid-cols-\\[1\\.35fr_0\\.65fr\\] {
          grid-template-columns: minmax(0, 1fr);
        }

        .kiosk-scan-page button,
        .kiosk-scan-page select,
        .kiosk-scan-page input {
          font-size: 22px;
        }

        .kiosk-scan-page .text-2xl {
          font-size: 30px;
        }

        .kiosk-scan-page .text-sm {
          font-size: 19px;
        }

        .kiosk-scan-page .text-xs {
          font-size: 17px;
        }

        .kiosk-document-list {
          position: fixed;
          right: 0;
          bottom: 0;
          left: 0;
          z-index: 20;
          height: 20vh;
          overflow: hidden;
          padding: 10px 24px 14px;
          background: rgba(255, 248, 243, .97);
          box-shadow: 0 -8px 24px rgba(117, 48, 27, .16);
        }

        .kiosk-document-list > aside {
          display: flex;
          flex-direction: column;
          height: 100%;
          box-sizing: border-box;
          max-height: none;
          margin: 0 auto;
          max-width: 1440px;
          border-radius: 18px;
        }

        .kiosk-document-list .document-list-header {
          flex: 0 0 auto;
        }

        .kiosk-document-list .document-list-items {
          min-height: 0;
          overflow-y: auto;
          padding-right: 4px;
        }

        .kiosk-scanned-files {
          min-height: 0;
          height: 75vh;
          max-height: none;
          margin-bottom: 0;
        }

        .kiosk-scanned-files > section {
          display: flex;
          flex-direction: column;
          height: auto;
          min-height: 0;
          max-height: none;
          margin-bottom: 0;
        }

        .kiosk-scanned-files .scanned-files-header {
          flex: 0 0 auto;
        }

        .kiosk-scanned-files .scanned-files-items {
          min-height: 0;
          overflow-y: auto;
          padding-right: 4px;
        }

        .kiosk-document-list .text-2xl {
          font-size: 26px;
        }

        .kiosk-document-list .text-sm {
          font-size: 18px;
        }

        .kiosk-document-list .text-xs {
          font-size: 16px;
        }

        .kiosk-scan-page main > div[class*="border-t"] {
          display: flex;
          flex-wrap: wrap;
          align-items: stretch;
          gap: 14px;
        }

        .kiosk-scan-page main > div[class*="border-t"] > div:first-child {
          flex: 1 1 360px;
          min-width: 300px;
        }

        .kiosk-scan-page main > div[class*="border-t"] > div:nth-child(2) {
          display: flex;
          flex: 1 1 520px;
          flex-wrap: wrap;
          gap: 12px;
        }

        .kiosk-action-buttons {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          align-items: end;
          gap: 12px;
          flex: 1 1 520px;
        }

        .kiosk-action-button {
          position: relative;
          min-width: 0;
        }

        .kiosk-action-button > button {
          width: 100%;
          min-width: 0;
        }

        .kiosk-action-button > .anticon {
          top: -2.25rem;
          left: 50%;
          right: auto;
          transform: translateX(-50%);
          pointer-events: none;
        }

        .kiosk-submit-button {
          min-height: 58px;
        }

        .kiosk-scan-page main > div[class*="border-t"] > div:nth-child(2) > div,
        .kiosk-scan-page main > div[class*="border-t"] > div:nth-child(2) > button {
          flex: 1 1 150px;
          min-width: 140px;
        }

        .kiosk-scan-page main > div[class*="border-t"] button {
          min-height: 58px;
          padding: 12px 18px;
          white-space: normal;
          line-height: 1.2;
        }

        .kiosk-scan-page main > div[class*="border-t"] select {
          min-width: 180px;
          min-height: 42px;
        }

        @media (min-width: 700px) and (max-width: 1399px) {
          .kiosk-scan-page > div {
            width: 100%;
            max-width: 1080px;
            min-height: 1920px;
            margin: 0 auto;
            padding: 24px 32px 40px;
          }

          .kiosk-scan-page header {
            margin-bottom: 24px;
            padding: 22px 30px;
          }

          .kiosk-scan-page main {
            padding: 28px;
          }

          .kiosk-scan-ai {
            min-height: 320px;
            padding: 20px 32px;
            margin-bottom: 24px;
          }

          .kiosk-scan-ai img {
            width: min(100%, 900px);
            height: 280px;
          }

          .kiosk-scan-page main > div[class*="border-t"] {
            flex-wrap: nowrap;
          }

          .kiosk-scan-page main > div[class*="border-t"] > div:nth-child(2),
          .kiosk-action-buttons {
            flex-wrap: nowrap;
          }

          .kiosk-scan-page main > div[class*="border-t"] > div:nth-child(2) > div,
          .kiosk-scan-page main > div[class*="border-t"] > div:nth-child(2) > button {
            min-width: 150px;
          }
        }

        @media (max-width: 699px) {
          .kiosk-scan-page > div {
            padding-left: 14px;
            padding-right: 14px;
          }

          .kiosk-document-list {
            padding: 8px 10px 10px;
          }

          .kiosk-action-buttons {
            grid-template-columns: 1fr;
          }

          .kiosk-action-button > .anticon {
            top: -1.9rem;
          }
        }

        @media (min-width: 1400px) {
          .kiosk-scan-page > div {
            min-height: 1080px;
            padding: 18px 42px 30px;
          }

          .kiosk-scan-page header {
            margin-bottom: 14px;
            padding: 14px 24px;
          }

          .kiosk-scan-page main {
            padding: 22px;
          }

          .kiosk-document-list {
            padding-left: 42px;
            padding-right: 42px;
          }
        }

        @media (min-width: 1000px) and (max-width: 1100px) and (min-height: 1800px) {
          .kiosk-scan-page,
          .kiosk-scan-page > div {
            height: 100vh;
            min-height: 0;
            overflow: hidden;
          }

          .kiosk-scan-page > div {
            padding: 18px 28px 0;
          }

          .kiosk-scan-page header {
            height: 108px;
            margin-bottom: 14px;
            padding: 16px 26px;
            box-sizing: border-box;
          }

          .kiosk-scan-ai {
            height: 252px;
            min-height: 0;
            margin-bottom: 16px;
            padding: 14px 28px;
          }

          .kiosk-scan-ai img {
            height: 220px;
          }

          .kiosk-scan-page main {
            height: calc(75vh - 408px);
            min-height: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
          }

          .kiosk-scan-page main > div[class*="border-t"] {
            flex: 0 0 136px;
            gap: 12px;
            padding-bottom: 16px;
          }

          .kiosk-scan-page main > div[class*="border-t"] > div:first-child {
            min-width: 0;
            flex: 1 1 330px;
          }

          .kiosk-scan-page main > div[class*="border-t"] > div:nth-child(2),
          .kiosk-action-buttons {
            min-width: 0;
            flex: 1 1 500px;
            gap: 10px;
          }

          .kiosk-scan-page main > div[class*="border-t"] button {
            min-height: 64px;
            padding: 12px 14px;
            font-size: 21px;
          }

          .kiosk-scan-page main > div[class*="border-t"] select {
            min-width: 0;
            min-height: 48px;
          }

          .kiosk-scan-page main > div.grid {
            flex: 1 1 auto;
            min-height: 0;
            gap: 16px;
            align-items: start;
          }

          .kiosk-scanned-files {
            height: auto;
            min-height: 0;
          }

          .kiosk-scanned-files > section {
            height: auto;
            padding: 18px;
          }

          .kiosk-scanned-files .scanned-files-items {
            flex: 0 1 auto;
            max-height: calc(75vh - 600px);
            grid-template-columns: repeat(4, minmax(0, 1fr));
            align-content: start;
          }

          .kiosk-document-list {
            height: 25vh;
            padding: 10px 28px 12px;
          }

          .kiosk-document-list > aside {
            padding: 16px;
          }
        }
      `}</style>
    </div>
  );
}

